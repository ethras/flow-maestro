"""Spec validation and apply commands."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import unified_diff
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.panel import Panel

from .state import (
    SPEC_MANIFEST_FILENAME,
    SPEC_MERGE_REPORT_FILENAME,
    archive_change,
    apply_deltas_to_spec,
    canonical_spec_path,
    change_delta_specs,
    change_dir,
    list_changes,
    default_spec_content,
    ensure_canonical_spec,
    DeltaParseResult,
    RequirementDelta,
    load_spec_index,
    parse_delta_markdown,
    project_dir,
    save_spec_index,
    slugify_identifier,
    spec_manifest_path,
    spec_merge_report_path,
    validate_delta_result,
)
from .utils import (
    append_timeline,
    console,
    locate_flow_dir,
    require_flow_dir,
    resolve_project,
)

specs_app = typer.Typer(help="Validate and apply spec deltas")


class SpecCommandError(RuntimeError):
    """Raised when spec helper operations fail."""


@dataclass
class CapabilityContext:
    name: str
    delta_path: Path
    canonical_path: Path
    parsed: DeltaParseResult
    current_text: str
    updated_text: str
    would_create: bool


@specs_app.command("status")
def specs_status(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
) -> None:
    """Show changes that contain delta specs and their preparation state."""

    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    rows: List[str] = []

    for change in list_changes(flow_path, project_slug):
        deltas = change_delta_specs(flow_path, project_slug, change)
        if not deltas:
            continue
        manifest = spec_manifest_path(flow_path, project_slug, change)
        report = spec_merge_report_path(flow_path, project_slug, change)
        rows.append(
            " · ".join(
                [
                    f"{change}",
                    f"specs={len(deltas)}",
                    f"manifest={'yes' if manifest.exists() else 'no'}",
                    f"prepared={_format_file_timestamp(manifest)}",
                    f"report={_format_file_timestamp(report)}",
                ]
            )
        )

    if not rows:
        console.print(Panel("No delta specs pending for this project.", border_style="green"))
        return

    console.print(
        Panel("\n".join(rows), title=f"Spec Status · {project_slug}", border_style="cyan")
    )


@specs_app.command("prepare")
def specs_prepare(
    change_id: str = typer.Argument(..., help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    diff: bool = typer.Option(True, "--diff/--no-diff", help="Write per-capability diff files"),
) -> None:
    """Generate a manifest + diff preview for the delta specs of a change."""

    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    try:
        contexts = _gather_capability_contexts(flow_path, project_slug, change_id)
    except SpecCommandError as exc:
        console.print(Panel(str(exc), border_style="red"))
        raise typer.Exit(1)

    spec_index = load_spec_index(flow_path, project_slug)
    manifest = _build_manifest(
        flow_path,
        project_slug,
        change_id,
        contexts,
        spec_index,
        write_diffs=diff,
    )
    manifest_path = spec_manifest_path(flow_path, project_slug, change_id)
    _write_manifest(manifest_path, manifest)
    change_path = change_dir(flow_path, project_slug, change_id)
    rel_manifest = manifest_path.relative_to(change_path)
    stats = manifest.get("stats", {})
    console.print(
        Panel(
            f"Prepared {stats.get('capabilities', 0)} capability delta(s); manifest at {rel_manifest}",
            border_style="green",
        )
    )


@specs_app.command("merge")
def specs_merge(
    change_id: str = typer.Argument(..., help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing"),
    finalize: bool = typer.Option(False, "--finalize", help="Archive the change after a successful merge"),
    diff: bool = typer.Option(False, "--diff/--no-diff", help="Refresh diff files before merging"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)

    try:
        contexts = _gather_capability_contexts(flow_path, project_slug, change_id)
    except SpecCommandError as exc:
        console.print(Panel(str(exc), border_style="red"))
        raise typer.Exit(1)

    spec_index = load_spec_index(flow_path, project_slug)
    manifest = _build_manifest(
        flow_path,
        project_slug,
        change_id,
        contexts,
        spec_index,
        write_diffs=diff,
    )
    manifest_path = spec_manifest_path(flow_path, project_slug, change_id)
    _write_manifest(manifest_path, manifest)

    results = _perform_merge(
        flow_path,
        project_slug,
        change_id,
        contexts,
        manifest,
        spec_index,
        dry_run=dry_run,
    )

    report_path = spec_merge_report_path(flow_path, project_slug, change_id)
    _write_merge_report(
        report_path,
        project_slug,
        change_id,
        results,
        dry_run=dry_run,
        finalized=bool(finalize and not dry_run),
    )

    summary = f"Merged {len(results)} capability delta(s)"
    if dry_run:
        summary = f"Dry run — {summary}"
    summary += f"; report at {report_path.name}"
    console.print(Panel(summary, border_style="green"))

    if finalize and dry_run:
        console.print(Panel("Cannot finalize during a dry run.", border_style="yellow"))
        return

    if finalize and not dry_run:
        change_path = change_dir(flow_path, project_slug, change_id)
        append_timeline(change_path, "specs.merge", "Merged delta specs into canonical specs")
        archive_change(flow_path, project_slug, change_id)
        console.print(Panel(f"Archived change '{change_id}'", border_style="cyan"))


@specs_app.command("rename-capability")
def specs_rename_capability(
    old: str = typer.Argument(..., help="Existing capability name"),
    new: str = typer.Argument(..., help="Target capability name"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    include_changes: bool = typer.Option(True, "--include-changes/--no-include-changes", help="Rename capability folders inside active change workspaces"),
) -> None:
    if old == new:
        console.print(Panel("Old and new capability names match.", border_style="yellow"))
        raise typer.Exit(1)

    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)

    canonical_old = canonical_spec_path(flow_path, project_slug, old).parent
    canonical_new = canonical_spec_path(flow_path, project_slug, new).parent
    if not canonical_old.exists():
        console.print(Panel(f"Capability '{old}' not found.", border_style="red"))
        raise typer.Exit(1)
    if canonical_new.exists():
        console.print(
            Panel(
                f"Capability '{new}' already exists. Merge specs manually, then remove the old folder.",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    canonical_new.parent.mkdir(parents=True, exist_ok=True)
    canonical_old.rename(canonical_new)

    spec_index = load_spec_index(flow_path, project_slug)
    updated = False
    for meta in spec_index.values():
        if meta.get("capability") == old:
            meta["capability"] = new
            updated = True
    if updated:
        save_spec_index(flow_path, project_slug, spec_index)

    warnings: List[str] = []
    if include_changes:
        for change in list_changes(flow_path, project_slug):
            change_specs = change_dir(flow_path, project_slug, change) / "specs"
            source = change_specs / old
            if not source.exists():
                continue
            target = change_specs / new
            if target.exists():
                warnings.append(f"{change}: target '{new}' already exists; skipped")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)

    message = f"Renamed capability '{old}' → '{new}'"
    if warnings:
        message += f" with {len(warnings)} warning(s)"
    console.print(Panel(message, border_style="green"))
    if warnings:
        console.print(Panel("\n".join(warnings), border_style="yellow"))


def _gather_capability_contexts(flow_path: Path, project_slug: str, change_id: str) -> List[CapabilityContext]:
    deltas = change_delta_specs(flow_path, project_slug, change_id)
    if not deltas:
        raise SpecCommandError("No delta specs to process.")

    contexts: List[CapabilityContext] = []
    errors: List[str] = []
    for capability, path in deltas:
        text = path.read_text(encoding="utf-8")
        try:
            parsed = parse_delta_markdown(text)
        except Exception as exc:  # pragma: no cover - parser already covered in tests
            errors.append(f"{capability}: {exc}")
            continue
        validation_errors = validate_delta_result(parsed)
        if validation_errors:
            errors.extend(f"{capability}: {err}" for err in validation_errors)
            continue

        target = canonical_spec_path(flow_path, project_slug, capability)
        if target.exists():
            current = target.read_text(encoding="utf-8")
            would_create = False
        else:
            current = default_spec_content(capability)
            would_create = True
        updated = apply_deltas_to_spec(current, parsed)
        contexts.append(
            CapabilityContext(
                name=capability,
                delta_path=path,
                canonical_path=target,
                parsed=parsed,
                current_text=current,
                updated_text=updated,
                would_create=would_create,
            )
        )

    if errors:
        raise SpecCommandError("\n".join(errors))
    return contexts


def _render_diff_text(capability: str, current: str, updated: str) -> str:
    lines = list(
        unified_diff(
            current.splitlines(),
            updated.splitlines(),
            fromfile=f"canonical/{capability}",
            tofile=f"preview/{capability}",
            lineterm="",
        )
    )
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def _find_requirement_identifier(delta: RequirementDelta) -> Optional[str]:
    for line in delta.body.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("requirement-id:"):
            value = stripped.split(":", 1)[1].strip()
            if value:
                return value
    return None


def _resolve_requirement_id(
    delta: RequirementDelta,
    capability: str,
    spec_index: Dict[str, Dict[str, str]],
    seen: set[str],
) -> str:
    explicit = _find_requirement_identifier(delta)
    candidate = slugify_identifier(explicit) if explicit else None
    existing_ids = set(spec_index.keys())

    if not candidate and delta.operation in {"MODIFIED", "REMOVED"}:
        for requirement_id, meta in spec_index.items():
            if meta.get("capability") == capability and meta.get("title") == delta.title:
                candidate = requirement_id
                break

    if not candidate:
        candidate = f"{slugify_identifier(capability)}.{slugify_identifier(delta.title)}"

    if delta.operation in {"MODIFIED", "REMOVED"} and candidate in existing_ids:
        return candidate

    if candidate not in seen:
        seen.add(candidate)
        return candidate

    base = candidate
    suffix = 2
    while f"{base}-{suffix}" in seen:
        suffix += 1
    deduped = f"{base}-{suffix}"
    seen.add(deduped)
    return deduped


def _build_manifest(
    flow_path: Path,
    project_slug: str,
    change_id: str,
    contexts: List[CapabilityContext],
    spec_index: Dict[str, Dict[str, str]],
    *,
    write_diffs: bool,
) -> Dict:
    change_path = change_dir(flow_path, project_slug, change_id)
    project_path = project_dir(flow_path, project_slug)
    seen_ids: set[str] = set(spec_index.keys())

    manifest = {
        "version": 1,
        "project": project_slug,
        "change_id": change_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capabilities": [],
    }

    requirement_total = 0
    diff_count = 0
    for ctx in contexts:
        diff_rel: Optional[str] = None
        if write_diffs:
            diff_text = _render_diff_text(ctx.name, ctx.current_text, ctx.updated_text)
            diff_file = ctx.delta_path.parent / "merge.diff"
            if diff_text:
                diff_file.write_text(diff_text, encoding="utf-8")
                diff_rel = str(diff_file.relative_to(change_path))
                diff_count += 1
            elif diff_file.exists():
                diff_file.unlink()

        delta_rel = str(ctx.delta_path.relative_to(change_path))
        canonical_rel = str(ctx.canonical_path.relative_to(project_path))
        entry = {
            "capability": ctx.name,
            "delta_path": delta_rel,
            "canonical_path": canonical_rel,
            "diff_path": diff_rel,
            "would_create": ctx.would_create,
            "preview_changed": ctx.updated_text != ctx.current_text,
            "requirements": [],
            "renames": [
                {"from": rename.old, "to": rename.new}
                for rename in ctx.parsed.renames
            ],
        }

        for op, deltas in ctx.parsed.requirements.items():
            for delta in deltas:
                requirement_id = _resolve_requirement_id(delta, ctx.name, spec_index, seen_ids)
                entry["requirements"].append(
                    {
                        "operation": op,
                        "title": delta.title,
                        "requirement_id": requirement_id,
                        "has_scenario": "#### Scenario:" in delta.body,
                    }
                )
        requirement_total += len(entry["requirements"])
        manifest["capabilities"].append(entry)

    manifest["stats"] = {
        "capabilities": len(contexts),
        "requirements": requirement_total,
        "diffs": diff_count,
    }
    return manifest


def _write_manifest(path: Path, manifest: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _apply_spec_index_updates(
    spec_index: Dict[str, Dict[str, str]],
    entry: Dict,
    change_id: str,
    timestamp: str,
) -> None:
    for requirement in entry.get("requirements", []):
        requirement_id = requirement["requirement_id"]
        if requirement["operation"] == "REMOVED":
            spec_index.pop(requirement_id, None)
        else:
            spec_index[requirement_id] = {
                "capability": entry["capability"],
                "title": requirement["title"],
                "updated_at": timestamp,
                "change_id": change_id,
            }


def _perform_merge(
    flow_path: Path,
    project_slug: str,
    change_id: str,
    contexts: List[CapabilityContext],
    manifest: Dict,
    spec_index: Dict[str, Dict[str, str]],
    *,
    dry_run: bool,
) -> List[Dict[str, object]]:
    entry_map = {entry["capability"]: entry for entry in manifest.get("capabilities", [])}
    timestamp = datetime.now(timezone.utc).isoformat()
    results: List[Dict[str, object]] = []

    for ctx in contexts:
        target = ctx.canonical_path
        changed = ctx.updated_text != ctx.current_text
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(ctx.updated_text, encoding="utf-8")
            entry = entry_map.get(ctx.name)
            if entry:
                _apply_spec_index_updates(spec_index, entry, change_id, timestamp)

        results.append(
            {
                "capability": ctx.name,
                "delta_path": str(ctx.delta_path),
                "canonical_path": str(target),
                "changed": changed,
                "would_create": ctx.would_create,
            }
        )

    if not dry_run:
        save_spec_index(flow_path, project_slug, spec_index)

    return results


def _write_merge_report(
    path: Path,
    project_slug: str,
    change_id: str,
    results: List[Dict[str, object]],
    *,
    dry_run: bool,
    finalized: bool,
) -> None:
    report = {
        "project": project_slug,
        "change_id": change_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "finalized": finalized,
        "results": results,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _format_file_timestamp(path: Path) -> str:
    if not path.exists():
        return "—"
    stamp = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return stamp.isoformat()




@specs_app.command("validate")
def specs_validate(
    change_id: str = typer.Argument(..., help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    deltas = change_delta_specs(flow_path, project_slug, change_id)
    if not deltas:
        console.print(Panel("No delta specs to validate.", border_style="yellow"))
        raise typer.Exit(1)

    errors = []
    for capability, path in deltas:
        text = path.read_text(encoding="utf-8")
        try:
            parsed = parse_delta_markdown(text)
        except Exception as exc:
            errors.append(f"{capability}: {exc}")
            continue
        for err in validate_delta_result(parsed):
            errors.append(f"{capability}: {err}")

    if errors:
        console.print(Panel("\n".join(errors), title="Validation Errors", border_style="red"))
        raise typer.Exit(1)

    console.print(Panel(f"Delta specs valid for change '{change_id}'", border_style="green"))


@specs_app.command("apply")
def specs_apply(
    change_id: str = typer.Argument(..., help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without writing"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    deltas = change_delta_specs(flow_path, project_slug, change_id)
    if not deltas:
        console.print(Panel("No delta specs to apply.", border_style="red"))
        raise typer.Exit(1)

    results = []
    for capability, path in deltas:
        text = path.read_text(encoding="utf-8")
        parsed = parse_delta_markdown(text)
        errors = validate_delta_result(parsed)
        if errors:
            console.print(Panel("\n".join(f"{capability}: {e}" for e in errors), border_style="red"))
            raise typer.Exit(1)
        target = canonical_spec_path(flow_path, project_slug, capability)
        if target.exists():
            current = target.read_text(encoding="utf-8")
        elif dry_run:
            current = default_spec_content(capability)
        else:
            current = ensure_canonical_spec(target, capability)
        updated = apply_deltas_to_spec(current, parsed)
        results.append((capability, updated))
        if not dry_run:
            target.write_text(updated, encoding="utf-8")

    if dry_run:
        console.print(Panel(f"Dry run: would update {len(results)} spec(s) and archive change '{change_id}'", border_style="yellow"))
        return

    change_path = change_dir(flow_path, project_slug, change_id)
    if not change_path.exists():
        console.print(Panel(f"Change '{change_id}' not found for project '{project_slug}'", border_style="red"))
        raise typer.Exit(1)
    append_timeline(change_path, "specs.apply", "Applied delta specs to canonical specs")
    archive_change(flow_path, project_slug, change_id)
    console.print(Panel(f"Applied {len(results)} spec(s) and archived change '{change_id}'", border_style="green"))
