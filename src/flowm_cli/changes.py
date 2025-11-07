"""Change management commands."""
from __future__ import annotations

from typing import List, Optional

import typer
from rich.panel import Panel

from .templates import PLAN_FILENAME, PLAN_TEMPLATE, SPEC_TEMPLATE, TASKS_TEMPLATE
from .utils import (
    append_timeline,
    console,
    locate_flow_dir,
    plan_path,
    require_flow_dir,
    resolve_change,
    resolve_project,
    save_session_change,
    write_if_missing,
)
from .state import change_delta_specs, ensure_change_structure, list_changes

changes_app = typer.Typer(help="Manage change folders")


@changes_app.command("list")
def changes_list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    changes = list_changes(flow_path, project_slug)
    if not changes:
        console.print(Panel(f"No active changes for {project_slug}", border_style="yellow"))
        return
    console.print(Panel("\n".join(changes), title=f"Changes - {project_slug}", border_style="green"))


@changes_app.command("init")
def changes_init(
    change_id: str = typer.Argument(..., help="Change identifier (kebab-case)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    capability: List[str] = typer.Option([], "--capability", "-c", help="Capability name to scaffold delta for"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    _, change_path = resolve_change(flow_path, project_slug, change_id, allow_create=True)

    spec_created = write_if_missing(
        change_path / "spec.md",
        SPEC_TEMPLATE.replace("{change_id}", change_id) + "\n",
    )
    plan_created = write_if_missing(
        change_path / PLAN_FILENAME,
        PLAN_TEMPLATE + "\n",
    )
    tasks_created = write_if_missing(
        change_path / "tasks.md",
        TASKS_TEMPLATE + "\n",
    )
    write_if_missing(change_path / "qa.md", "")
    write_if_missing(change_path / "timeline.jsonl", "")

    for cap in capability:
        delta_path = change_path / "specs" / cap / "spec.md"
        delta_template = (
            "## ADDED Requirements\n"
            "### Requirement: Placeholder\n"
            "Describe the requirement.\n\n"
            "#### Scenario: Primary success\n"
            "- **WHEN** ...\n"
            "- **THEN** ...\n"
        )
        write_if_missing(delta_path, delta_template)

    save_session_change(flow_path, project_slug, change_id, stage="ideate")
    append_timeline(change_path, "changes.init", "Initialized change workspace")

    created_assets = [
        name
        for flag, name in zip(
            [spec_created, plan_created, tasks_created],
            ["spec.md", PLAN_FILENAME, "tasks.md"],
        )
        if flag
    ]
    summary = ", ".join(created_assets) if created_assets else "Existing files preserved"
    console.print(Panel(f"Change '{change_id}' ready in project '{project_slug}'.\n{summary}", border_style="green"))


@changes_app.command("show")
def changes_show(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    change_slug, change_path = resolve_change(flow_path, project_slug, change_id)
    change_path = ensure_change_structure(flow_path, project_slug, change_slug)
    spec_paths = change_delta_specs(flow_path, project_slug, change_slug)
    info_lines = [f"Change path: {change_path}"]
    if spec_paths:
        info_lines.append("Delta specs:")
        info_lines.extend([f" - {cap}: {path}" for cap, path in spec_paths])
    else:
        info_lines.append("No delta specs yet.")
    console.print(Panel("\n".join(info_lines), title=f"Change - {change_slug}", border_style="green"))


