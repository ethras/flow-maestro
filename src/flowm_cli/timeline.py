"""Timeline inspection and logging commands."""
from __future__ import annotations

import json
from typing import Optional

import typer
from rich.panel import Panel

from .utils import (
    append_timeline,
    console,
    locate_flow_dir,
    require_flow_dir,
    resolve_change,
    resolve_project,
)

timeline_app = typer.Typer(help="Inspect or append timeline events")


@timeline_app.command("show")
def timeline_show(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    limit: int = typer.Option(0, "--limit", "-n", help="Show only the most recent N entries"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    change_slug, change_path = resolve_change(flow_path, project_slug, change_id)

    timeline_path = change_path / "timeline.jsonl"
    if not timeline_path.exists():
        console.print(Panel(f"No timeline found at {timeline_path}", border_style="yellow"))
        return

    events = []
    for line in timeline_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"timestamp": "", "command": "invalid", "summary": line})

    if not events:
        console.print(Panel("Timeline is empty.", border_style="yellow"))
        return

    if limit > 0:
        events = events[-limit:]

    lines = [
        f"{event.get('timestamp', '')} - {event.get('command', '')} - {event.get('summary', '')}"
        for event in events
    ]
    console.print(Panel("\n".join(lines), title=f"Timeline - {change_slug}", border_style="green"))


@timeline_app.command("log")
def timeline_log(
    summary: str = typer.Argument(..., help="Summary to append"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    change_id: Optional[str] = typer.Option(None, "--change", "-c", help="Change identifier"),
    command: str = typer.Option("timeline.log", "--command", "-m", help="Command label to record"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    _, change_path = resolve_change(flow_path, project_slug, change_id)

    append_timeline(change_path, command, summary)
    console.print(Panel(f"Timeline updated: {summary}", title="Timeline", border_style="green"))


