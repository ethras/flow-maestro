"""Project-related CLI commands."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import typer
from rich.panel import Panel

from .core import ensure_dir
from .state import list_projects, project_dir, save_projects
from .templates import CONSTITUTION_TEMPLATE
from .utils import (
    console,
    load_projects_data,
    locate_flow_dir,
    require_flow_dir,
    resolve_project,
    save_session_project,
    write_if_missing,
)

ConstitutionSection = Tuple[str, str, bool]

CONSTITUTION_SECTIONS: Dict[str, ConstitutionSection] = {
    "core": ("## Core Architecture", "Last verified", False),
    "data": ("## Data & Integrations", "Last verified", False),
    "operations": ("## Operational Guardrails", "Last verified", False),
    "risks": ("## Risks & Mitigations", "Last verified", False),
    "watchlist": ("## Watchlist", "Last reviewed", True),
}

projects_app = typer.Typer(help="Manage Flow Maestro projects")
constitution_app = typer.Typer(help="Record reusable findings in the project constitution")
projects_app.add_typer(constitution_app, name="constitution")


@projects_app.command("list")
def projects_list() -> None:
    """List registered projects."""
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    projects = load_projects_data(flow_path)
    if not projects:
        console.print(Panel("No projects registered.", border_style="yellow"))
        return
    lines = [f"{slug} - {meta.get('path', 'unknown')}" for slug, meta in list_projects(flow_path)]
    console.print(Panel("\n".join(lines), title="Projects", border_style="green"))


@projects_app.command("add")
def projects_add(
    slug: str = typer.Argument(..., help="Project identifier (kebab-case recommended)"),
    path: Path = typer.Option(Path("."), "--path", help="Path to project root"),
    name: Optional[str] = typer.Option(None, "--name", help="Friendly project name"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    projects = load_projects_data(flow_path)
    if slug in projects:
        console.print(Panel(f"Project '{slug}' already exists.", border_style="red"))
        raise typer.Exit(1)
    abs_path = (flow_path.parent / path).resolve() if not path.is_absolute() else path.resolve()
    projects[slug] = {
        "name": name or slug.replace("-", " ").title(),
        "path": str(abs_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_projects(flow_path, projects)
    project_root = project_dir(flow_path, slug)
    ensure_dir(project_root)
    ensure_dir(project_root / "changes")
    ensure_dir(project_root / "changes" / "archive")
    ensure_dir(project_root / "specs")
    write_if_missing(
        project_root / "constitution.md",
        CONSTITUTION_TEMPLATE.replace("{project_slug}", slug) + "\n",
    )
    save_session_project(flow_path, slug)
    console.print(Panel(f"Registered project '{slug}' ({abs_path})", border_style="green"))


@projects_app.command("use")
def projects_use(slug: Optional[str] = typer.Argument(None, help="Project slug to activate")) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    resolved = resolve_project(flow_path, slug)
    console.print(Panel(f"Active project: {resolved}", border_style="green"))


@constitution_app.command("record")
def constitution_record(
    title: str = typer.Argument(..., help="Entry title"),
    summary: str = typer.Option(..., "--summary", "-s", prompt=True, help="1-2 sentence description"),
    source: str = typer.Option(..., "--source", "-S", prompt=True, help="Reference like change-id/path:line"),
    section: str = typer.Option(
        "core",
        "--section",
        "-c",
        case_sensitive=False,
        help="Target section: core, data, operations, risks, watchlist",
    ),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    verified: Optional[str] = typer.Option(
        None,
        "--verified",
        "-v",
        help="Verification date (defaults to today, YYYY-MM-DD)",
    ),
    owner: Optional[str] = typer.Option(
        None,
        "--owner",
        "-o",
        help="Watchlist owner (required when section=watchlist)",
    ),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)

    normalized_section = section.lower()
    if normalized_section not in CONSTITUTION_SECTIONS:
        available = ", ".join(sorted(CONSTITUTION_SECTIONS))
        console.print(
            Panel(
                f"Unknown section '{section}'. Choose from: {available}",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    if normalized_section == "watchlist" and not owner:
        console.print(Panel("--owner is required for the watchlist section", border_style="red"))
        raise typer.Exit(1)

    verification_date = _resolve_verification_date(verified)
    entry_summary = " ".join(summary.split())
    entry_source = source.strip()
    if not entry_source:
        console.print(Panel("--source cannot be empty", border_style="red"))
        raise typer.Exit(1)

    constitution_path = project_dir(flow_path, project_slug) / "constitution.md"
    write_if_missing(
        constitution_path,
        CONSTITUTION_TEMPLATE.replace("{project_slug}", project_slug) + "\n",
    )

    upserted = _upsert_constitution_entry(
        constitution_path,
        normalized_section,
        title.strip(),
        entry_summary,
        entry_source,
        verification_date,
        owner.strip() if owner else None,
    )

    action = "Updated" if upserted else "Appended"
    console.print(
        Panel(
            f"{action} '{title}' in {constitution_path}",
            title=f"Constitution · {project_slug}",
            border_style="green",
        )
    )


def _resolve_verification_date(candidate: Optional[str]) -> str:
    if candidate:
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
        except ValueError:
            console.print(
                Panel(
                    "--verified must be provided as YYYY-MM-DD",
                    border_style="red",
                )
            )
            raise typer.Exit(1)
        return candidate
    return datetime.now(timezone.utc).date().isoformat()


def _ensure_section(lines: List[str], header: str) -> Tuple[int, int]:
    for idx, line in enumerate(lines):
        if line.strip() == header:
            return idx, _section_end(lines, idx)
    if lines and lines[-1].strip():
        lines.append("")
    lines.append(header)
    lines.append("")
    start = len(lines) - 2
    return start, len(lines)


def _section_end(lines: List[str], start_idx: int) -> int:
    idx = start_idx + 1
    while idx < len(lines):
        if lines[idx].startswith("## "):
            break
        idx += 1
    return idx


def _remove_existing_entry(
    lines: List[str],
    start_idx: int,
    end_idx: int,
    title: str,
) -> Tuple[bool, int]:
    idx = start_idx + 1
    lowered = title.lower()
    while idx < end_idx:
        line = lines[idx]
        if line.startswith("- Title: "):
            current_title = line[len("- Title: ") :].strip().lower()
            block_start = idx
            idx += 1
            while idx < end_idx and not lines[idx].startswith("- Title: ") and not lines[idx].startswith("## "):
                idx += 1
            block_end = idx
            if current_title == lowered:
                del lines[block_start:block_end]
                return True, _section_end(lines, start_idx)
            continue
        idx += 1
    return False, end_idx


def _build_entry_lines(
    section_key: str,
    title: str,
    summary: str,
    source: str,
    verified: str,
    owner: Optional[str],
) -> List[str]:
    _header, date_label, needs_owner = CONSTITUTION_SECTIONS[section_key]
    entry = [f"- Title: {title}", f"  - Summary: {summary}"]
    if needs_owner:
        entry.append(f"  - Owner: {owner}")
    entry.append(f"  - Source: {source}")
    entry.append(f"  - {date_label}: {verified}")
    return entry


def _upsert_constitution_entry(
    path: Path,
    section_key: str,
    title: str,
    summary: str,
    source: str,
    verified: str,
    owner: Optional[str],
) -> bool:
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = content.splitlines()
    if not lines:
        header = CONSTITUTION_SECTIONS[section_key][0]
        lines = [header, ""]

    header = CONSTITUTION_SECTIONS[section_key][0]
    start_idx, end_idx = _ensure_section(lines, header)
    replaced, end_idx = _remove_existing_entry(lines, start_idx, end_idx, title)

    entry_lines = _build_entry_lines(section_key, title, summary, source, verified, owner)
    insertion = entry_lines + [""]
    if end_idx > start_idx + 1 and lines[end_idx - 1].strip():
        insertion = [""] + insertion
    lines[end_idx:end_idx] = insertion

    text = "\n".join(lines).rstrip() + "\n"
    path.write_text(text, encoding="utf-8")
    return replaced
