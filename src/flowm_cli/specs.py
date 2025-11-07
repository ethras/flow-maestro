"""Spec validation and apply commands."""
from __future__ import annotations

from typing import Optional

import typer
from rich.panel import Panel

from .state import (
    archive_change,
    apply_deltas_to_spec,
    canonical_spec_path,
    change_delta_specs,
    change_dir,
    default_spec_content,
    ensure_canonical_spec,
    parse_delta_markdown,
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


