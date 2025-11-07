"""Project-related CLI commands."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

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

projects_app = typer.Typer(help="Manage Flow Maestro projects")


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

