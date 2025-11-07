"""Quality checks for change artifacts."""
from __future__ import annotations

from typing import List, Optional

import typer
from rich.panel import Panel

from .templates import PLACEHOLDER_PATTERNS
from .utils import (
    append_timeline,
    console,
    locate_flow_dir,
    plan_path,
    require_flow_dir,
    resolve_change,
    resolve_project,
)

quality_app = typer.Typer(help="Quality checks for change artifacts")


@quality_app.command("check")
def quality_check(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    include: List[str] = typer.Option([], "--include", "-i", help="Files to lint: spec, plan, tasks (alias: blueprint)"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    change_slug, change_path = resolve_change(flow_path, project_slug, change_id)

    targets = {
        "spec": change_path / "spec.md",
        "plan": plan_path(change_path),
        "tasks": change_path / "tasks.md",
    }
    aliases = {"blueprint": "plan"}
    requested = [item.lower() for item in include if item]
    candidate_keys = requested or list(targets.keys())
    normalized: List[str] = []
    unknown: List[str] = []
    for key in candidate_keys:
        canonical = aliases.get(key, key)
        if canonical not in targets:
            unknown.append(key)
        elif canonical not in normalized:
            normalized.append(canonical)
    if unknown:
        console.print(Panel(f"Unknown target(s): {', '.join(sorted(set(unknown)))}", border_style="red"))
        raise typer.Exit(1)

    issues: List[str] = []
    for key in (normalized or list(targets.keys())):
        path = targets[key]
        if not path.exists():
            issues.append(f"{key}: missing file ({path})")
            continue
        content = path.read_text(encoding="utf-8")
        file_issues: List[str] = []
        for marker, description in PLACEHOLDER_PATTERNS.items():
            if marker in content:
                file_issues.append(f"{description} -> '{marker}'")
        if "TODO" in content:
            file_issues.append("contains TODO marker")
        if "TBD" in content:
            file_issues.append("contains TBD marker")
        if file_issues:
            formatted = "; ".join(file_issues)
            issues.append(f"{key}: {formatted}")

    status = "warnings" if issues else "clear"
    append_timeline(change_path, "quality.check", f"Quality check {status}")

    if issues:
        console.print(
            Panel(
                "\n".join(issues),
                title=f"Quality warnings - {change_slug}",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    console.print(Panel(f"No placeholder markers detected for {', '.join(normalized or targets.keys())}", border_style="green"))


