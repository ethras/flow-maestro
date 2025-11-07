"""Research helpers for change folders."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

import typer
from rich.panel import Panel

from .utils import (
    append_timeline,
    console,
    locate_flow_dir,
    project_source_path,
    require_flow_dir,
    resolve_change,
    resolve_project,
    run_tool,
    save_session_change,
)

research_app = typer.Typer(help="Capture change research context")


@research_app.command("capture")
def research_capture(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    query: List[str] = typer.Option([], "--query", "-q", help="Repeat for each ripgrep pattern to capture"),
    commits: int = typer.Option(5, "--commits", "-c", min=0, help="Number of recent commits to record"),
) -> None:
    flow_path = locate_flow_dir()
    require_flow_dir(flow_path)
    project_slug = resolve_project(flow_path, project)
    change_slug, change_path = resolve_change(flow_path, project_slug, change_id)
    source_path = project_source_path(flow_path, project_slug)
    if not source_path.exists():
        console.print(Panel(f"Project path does not exist: {source_path}", border_style="red"))
        raise typer.Exit(1)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections: List[str] = [f"## Snapshot - {timestamp}", ""]

    if commits:
        git_log = run_tool(
            ["git", "log", f"-{commits}", "--pretty=format:%h %ad %s", "--date=short"],
            source_path,
        )
        if git_log:
            sections.append("### Recent Commits")
            sections.append("")
            sections.extend(f"- {line.strip()}" for line in git_log.splitlines() if line.strip())
            sections.append("")

    git_status = run_tool(["git", "status", "-sb"], source_path)
    if git_status:
        sections.append("### Git Status")
        sections.append("")
        sections.append("```\n" + git_status + "\n```")
        sections.append("")

    for pattern in query:
        rg_output = run_tool(
            ["rg", "--max-count", "20", "--line-number", "--color", "never", pattern],
            source_path,
        )
        sections.append(f"### Code Search - {pattern}")
        sections.append("")
        sections.append("```\n" + (rg_output or "(no matches)") + "\n```")
        sections.append("")

    research_path = change_path / "notes" / "research.md"
    research_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = "\n".join(sections).strip() + "\n"
    if research_path.exists():
        existing = research_path.read_text(encoding="utf-8").rstrip()
        separator = "\n\n" if existing else ""
        research_path.write_text(existing + separator + snapshot, encoding="utf-8")
    else:
        research_path.write_text("# Research Notes\n\n" + snapshot, encoding="utf-8")

    save_session_change(flow_path, project_slug, change_slug, stage="blueprint")
    query_count = len(query)
    plural = "query" if query_count == 1 else "queries"
    append_timeline(
        change_path,
        "research.capture",
        f"Captured research snapshot ({query_count} {plural})",
    )
    console.print(
        Panel(
            f"Research snapshot appended to {research_path}",
            title=f"Research - {change_slug}",
            border_style="green",
        )
    )

