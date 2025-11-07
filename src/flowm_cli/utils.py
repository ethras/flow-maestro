"""Shared helpers for Flow Maestro CLI modules."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

import httpx
import typer
from rich.console import Console
from rich.panel import Panel

from .constants import OWNER, REPO
from .core import ensure_dir, flow_dir
from .state import (
    change_dir,
    ensure_change_structure,
    list_projects,
    load_projects,
    load_session,
    project_dir,
    save_projects,
    save_session,
    state_dir,
)
from .templates import CONSTITUTION_TEMPLATE, LEGACY_BLUEPRINT_FILENAME, PLAN_FILENAME

console = Console()


# ---------------------------------------------------------------------------
# HTTP helpers

def auth_headers(token: Optional[str]) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def http_client(skip_tls: bool) -> httpx.Client:
    verify = False if skip_tls else True
    return httpx.Client(verify=verify, timeout=60)


def release_api_url(source: Optional[str]) -> str:
    if not source or source == "latest":
        return f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
    return f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{source}"


def pick_asset(release_json: dict, asset_name: str) -> Optional[dict]:
    for asset in release_json.get("assets", []) or []:
        if asset.get("name") == asset_name:
            return asset
    return None


def download_asset(url: str, client: httpx.Client, token: Optional[str], dest: Path) -> None:
    with client.stream("GET", url, headers=auth_headers(token), follow_redirects=True) as response:
        response.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in response.iter_bytes():
                fh.write(chunk)


# ---------------------------------------------------------------------------
# Filesystem helpers

def project_root(here: bool, path: Optional[Path]) -> Path:
    if path:
        return path.resolve()
    return Path.cwd() if here else Path.cwd()


def locate_flow_dir(start: Optional[Path] = None) -> Path:
    start = start or Path.cwd()
    for candidate in [start, *start.parents]:
        candidate_flow = flow_dir(candidate)
        if candidate_flow.exists():
            return candidate_flow
    return flow_dir(start)


def plan_path(change_path: Path) -> Path:
    plan = change_path / PLAN_FILENAME
    legacy = change_path / LEGACY_BLUEPRINT_FILENAME
    if plan.exists():
        return plan
    if legacy.exists():
        return legacy
    return plan


def require_flow_dir(flow_path: Path) -> None:
    if not flow_path.exists():
        console.print(Panel(".flow-maestro not found. Run 'flowm init' first.", border_style="red"))
        raise typer.Exit(1)


def ensure_state_files(flow_path: Path) -> None:
    ensure_dir(flow_path)
    ensure_dir(state_dir(flow_path))
    projects = list_projects(flow_path)
    for slug, _ in projects:
        proj_root = project_dir(flow_path, slug)
        if proj_root.exists():
            write_if_missing(
                proj_root / "constitution.md",
                CONSTITUTION_TEMPLATE.replace("{project_slug}", slug) + "\n",
            )


def load_projects_data(flow_path: Path) -> dict:
    ensure_state_files(flow_path)
    return load_projects(flow_path)


def load_session_data(flow_path: Path) -> dict:
    ensure_state_files(flow_path)
    return load_session(flow_path)


def save_session_project(flow_path: Path, slug: str) -> None:
    session = load_session_data(flow_path)
    session["project"] = slug
    save_session(flow_path, session)


def save_session_change(flow_path: Path, project: str, change_id: str, stage: str) -> None:
    session = load_session_data(flow_path)
    session["project"] = project
    session["change"] = change_id
    session["stage"] = stage
    save_session(flow_path, session)


def append_timeline(change_path: Path, command_name: str, summary: str) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command_name,
        "summary": summary,
    }
    timeline = change_path / "timeline.jsonl"
    timeline.parent.mkdir(parents=True, exist_ok=True)
    with timeline.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def resolve_project(flow_path: Path, requested: Optional[str]) -> str:
    projects = load_projects_data(flow_path)
    if not projects:
        console.print(Panel("No projects registered. Use 'flowm projects add <slug>' first.", border_style="red"))
        raise typer.Exit(1)
    if requested:
        if requested not in projects:
            console.print(Panel(f"Unknown project '{requested}'.", border_style="red"))
            raise typer.Exit(1)
        save_session_project(flow_path, requested)
        return requested

    session = load_session_data(flow_path)
    current = session.get("project")
    if current and current in projects:
        return current

    cwd = Path.cwd().resolve()
    matches: List[str] = []
    for slug, meta in projects.items():
        project_path = Path(meta.get("path") or "").resolve()
        try:
            cwd.relative_to(project_path)
        except Exception:
            continue
        matches.append(slug)

    if len(matches) == 1:
        slug = matches[0]
        save_session_project(flow_path, slug)
        return slug

    if len(projects) == 1:
        slug = next(iter(projects))
        save_session_project(flow_path, slug)
        return slug

    console.print(Panel("Select a project:", title="Projects", border_style="cyan"))
    for slug, meta in projects.items():
        console.print(f" - {slug} ({meta.get('path', 'unknown')})")
    slug = typer.prompt("Project slug")
    if slug not in projects:
        console.print(Panel(f"Unknown project '{slug}'.", border_style="red"))
        raise typer.Exit(1)
    save_session_project(flow_path, slug)
    return slug


def resolve_change(
    flow_path: Path,
    project_slug: str,
    change_id: Optional[str],
    allow_create: bool = False,
) -> Tuple[str, Path]:
    if not change_id:
        session = load_session_data(flow_path)
        change_id = session.get("change")
    if not change_id:
        console.print(Panel("No change specified or active.", border_style="red"))
        raise typer.Exit(1)

    if allow_create:
        change_path = ensure_change_structure(flow_path, project_slug, change_id)
    else:
        change_path = change_dir(flow_path, project_slug, change_id)
        if not change_path.exists():
            console.print(
                Panel(
                    f"Change '{change_id}' not found for project '{project_slug}'",
                    border_style="red",
                )
            )
            raise typer.Exit(1)
    return change_id, change_path


def project_source_path(flow_path: Path, project_slug: str) -> Path:
    projects = load_projects_data(flow_path)
    meta = projects.get(project_slug) or {}
    path_str = meta.get("path")
    if not path_str:
        console.print(
            Panel(
                f"Project '{project_slug}' is missing a source path. Re-run 'flowm projects add'.",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    return Path(path_str).resolve()


def run_tool(cmd: List[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return f"(command not found: {cmd[0]})"
    output = result.stdout.strip()
    if result.returncode != 0:
        err = result.stderr.strip()
        message = err or output
        return f"({' '.join(cmd)}) exited with {result.returncode}: {message}"
    if len(output) > 4000:
        output = output[:4000] + "\n... trimmed"
    return output


__all__ = [
    "append_timeline",
    "auth_headers",
    "console",
    "download_asset",
    "ensure_state_files",
    "http_client",
    "locate_flow_dir",
    "pick_asset",
    "plan_path",
    "project_root",
    "project_source_path",
    "release_api_url",
    "resolve_change",
    "resolve_project",
    "run_tool",
    "save_session_change",
    "save_session_project",
    "write_if_missing",
]
