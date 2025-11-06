#!/usr/bin/env python3
"""Flow Maestro Installer CLI (flowm)

Commands:
  - init:   install/update .flow-maestro from latest (or specified) release asset
  - update: update existing installation conservatively
  - link:   create project-local wrappers in .flow-maestro/bin
  - info:   show installed version and counts
  - version:show CLI version

Follows patterns from github/spec-kit's specify_cli with a smaller surface.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
import shutil

import httpx
import typer
from rich.console import Console
from rich.panel import Panel

from .core import (
    ASSET_NAME,
    compute_manifest,
    ensure_dir,
    ensure_readme,
    extract_zip_to_dir,
    flow_dir,
    load_manifest,
    merge_tree,
    read_version,
    save_manifest,
    write_version,
)

from .state import (
    StateError,
    archive_change,
    apply_deltas_to_spec,
    canonical_spec_path,
    change_delta_specs,
    change_dir,
    default_spec_content,
    ensure_canonical_spec,
    ensure_change_structure,
    list_changes,
    list_projects,
    load_projects,
    load_session,
    parse_delta_markdown,
    project_dir,
    save_projects,
    save_session,
    state_dir,
    validate_delta_result,
)

APP_NAME = "flowm"
__version__ = "0.4.0"
OWNER = os.getenv("FLOWM_REPO_OWNER", "ethras")
REPO = os.getenv("FLOWM_REPO_NAME", "flow-maestro")

console = Console()
app = typer.Typer(name=APP_NAME, add_completion=False)

projects_app = typer.Typer(help="Manage Flow Maestro projects")
changes_app = typer.Typer(help="Manage change folders")
specs_app = typer.Typer(help="Validate and apply spec deltas")
research_app = typer.Typer(help="Capture change research context")
quality_app = typer.Typer(help="Quality checks for change artifacts")
timeline_app = typer.Typer(help="Inspect or append timeline events")

app.add_typer(projects_app, name="projects")
app.add_typer(changes_app, name="changes")
app.add_typer(specs_app, name="specs")
app.add_typer(research_app, name="research")
app.add_typer(quality_app, name="quality")
app.add_typer(timeline_app, name="timeline")

SPEC_TEMPLATE = (
    "# Change: {change_id}\\n\\n"
    "## Overview\\n"
    "- Problem summary: <describe the gap or opportunity>\\n"
    "- Impacted users or teams: <list primary audiences>\\n\\n"
    "## Core Features\\n"
    "- Feature concept: <behaviour change in one sentence>\\n\\n"
    "## Data & Interfaces\\n"
    "- Data touchpoints: <APIs, schemas, events>\\n\\n"
    "## Architecture Highlights\\n"
    "- Integration notes: <systems, services, or boundaries>\\n\\n"
    "## Technical Decisions\\n"
    "- Decision: <choice> - Rationale: <why>\\n\\n"
    "## Environment Variables\\n"
    "- Env var: <VARIABLE_NAME>=<purpose and owner>\\n\\n"
    "## Open Questions\\n"
    "- [NEEDS CLARIFICATION: <question or assumption>]\\n\\n"
    "## Success Criteria\\n"
    "- Success signal: <how we'll measure success>\\n"
)

PLAN_TEMPLATE = (
    "# Implementation Plan\\n\\n"
    "## Summary\\n"
    "- Problem: <one sentence recap>\\n"
    "- Desired outcome: <target state>\\n"
    "- Confidence: <risk level or blockers>\\n\\n"
    "## Research & Discovery\\n"
    "- Code search highlights: <files, commands, references>\\n"
    "- Existing flows to audit: <entry points>\\n"
    "- External references: <docs, tickets, context>\\n\\n"
    "## Implementation Phases\\n"
    "- Phase 1: <focus and owner>\\n"
    "- Phase 2: <follow-on work>\\n\\n"
    "## Tests & Validation\\n"
    "- Automated: <commands to run>\\n"
    "- Manual: <scenarios or sign-off steps>\\n\\n"
    "## Risks & Mitigations\\n"
    "- Risk: <issue> - Mitigation: <contingency>\\n\\n"
    "## Follow-ups\\n"
    "- <documentation, rollout, comms, telemetry>\\n"
)

TASKS_TEMPLATE = (
    "## Phase 0 - Discovery\\n"
    "- [ ] 0.1 Capture baseline context in `notes/research.md`\\n"
    "  - Summary: <link relevant findings>\\n"
    "- [ ] 0.2 Align scope and constraints\\n"
    "  - Notes: <stakeholders or decisions>\\n\\n"
    "## Phase 1 - Implementation\\n"
    "- [ ] 1.1 Primary change track\\n"
    "  - Targets: <files or modules>\\n"
    "  - Verification: <quick checks during build>\\n"
    "- [ ] 1.2 Extend or add tests\\n"
    "  - Targets: <test paths>\\n"
    "  - Assertions: <behaviour to prove>\\n\\n"
    "## Phase 2 - Verification\\n"
    "- [ ] 2.1 Automated validation (`uv run pytest -q`, linters)\\n"
    "- [ ] 2.2 Manual scenario walkthrough\\n"
    "  - Steps: <user journey or edge cases>\\n\\n"
    "## Phase 3 - Follow-up\\n"
    "- [ ] 3.1 Documentation or changelog updates\\n"
    "- [ ] 3.2 Notify stakeholders / handoff\\n"
)

PLACEHOLDER_PATTERNS = {
    "<describe the gap or opportunity>": "spec overview placeholder",
    "<list primary audiences>": "spec overview placeholder",
    "<behaviour change in one sentence>": "core feature placeholder",
    "<APIs, schemas, events>": "data and interface placeholder",
    "<systems, services, or boundaries>": "architecture placeholder",
    "<choice>": "decision placeholder",
    "<why>": "decision rationale placeholder",
    "<VARIABLE_NAME>": "environment variable placeholder",
    "<purpose and owner>": "environment variable placeholder",
    "<question or assumption>": "open question placeholder",
    "<how we'll measure success>": "success criteria placeholder",
    "<one sentence recap>": "plan summary placeholder",
    "<target state>": "plan summary placeholder",
    "<risk level or blockers>": "plan summary placeholder",
    "<files, commands, references>": "research placeholder",
    "<entry points>": "research placeholder",
    "<docs, tickets, context>": "research placeholder",
    "<focus and owner>": "phase planning placeholder",
    "<follow-on work>": "phase planning placeholder",
    "<commands to run>": "validation placeholder",
    "<scenarios or sign-off steps>": "validation placeholder",
    "<issue>": "risk placeholder",
    "<contingency>": "risk placeholder",
    "<documentation, rollout, comms, telemetry>": "follow-up placeholder",
    "<link relevant findings>": "discovery placeholder",
    "<stakeholders or decisions>": "discovery placeholder",
    "<files or modules>": "implementation placeholder",
    "<quick checks during build>": "implementation placeholder",
    "<test paths>": "implementation placeholder",
    "<behaviour to prove>": "implementation placeholder",
    "<user journey or edge cases>": "verification placeholder",
}


def _auth_headers(token: Optional[str]) -> dict:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _http_client(skip_tls: bool) -> httpx.Client:
    verify = False if skip_tls else True
    return httpx.Client(verify=verify, timeout=60)


def _release_api_url(source: Optional[str]) -> str:
    if not source or source == "latest":
        return f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
    return f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{source}"


def _pick_asset(release_json: dict, asset_name: str) -> Optional[dict]:
    for a in release_json.get("assets", []) or []:
        if a.get("name") == asset_name:
            return a
    return None


def _download_asset(url: str, client: httpx.Client, token: Optional[str], dest: Path) -> None:
    with client.stream("GET", url, headers=_auth_headers(token), follow_redirects=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)


def _project_root(here: bool, path: Optional[Path]) -> Path:
    if path:
        return path.resolve()
    return Path.cwd()


def _locate_flow_dir(start: Optional[Path] = None) -> Path:
    start = start or Path.cwd()
    for candidate in [start, *start.parents]:
        candidate_flow = flow_dir(candidate)
        if candidate_flow.exists():
            return candidate_flow
    return flow_dir(start)


def _require_flow_dir(flow_path: Path) -> None:
    if not flow_path.exists():
        console.print(Panel(".flow-maestro not found. Run 'flowm init' first.", border_style="red"))
        raise typer.Exit(1)


def _ensure_state_files(flow_path: Path) -> None:
    ensure_dir(flow_path)
    ensure_dir(state_dir(flow_path))


def _load_projects_data(flow_path: Path) -> dict:
    _ensure_state_files(flow_path)
    return load_projects(flow_path)


def _load_session_data(flow_path: Path) -> dict:
    _ensure_state_files(flow_path)
    return load_session(flow_path)


def _save_session_project(flow_path: Path, slug: str) -> None:
    session = _load_session_data(flow_path)
    session["project"] = slug
    save_session(flow_path, session)


def _save_session_change(flow_path: Path, project: str, change_id: str, stage: str = "ideate") -> None:
    session = _load_session_data(flow_path)
    session["project"] = project
    session["change"] = change_id
    session["stage"] = stage
    save_session(flow_path, session)


def _append_timeline(change_path: Path, command_name: str, summary: str) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command_name,
        "summary": summary,
    }
    timeline = change_path / "timeline.jsonl"
    timeline.parent.mkdir(parents=True, exist_ok=True)
    with timeline.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def _write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _resolve_project(flow_path: Path, requested: Optional[str]) -> str:
    projects = _load_projects_data(flow_path)
    if not projects:
        console.print(Panel("No projects registered. Use 'flowm projects add <slug>' first.", border_style="red"))
        raise typer.Exit(1)
    if requested:
        if requested not in projects:
            console.print(Panel(f"Unknown project '{requested}'.", border_style="red"))
            raise typer.Exit(1)
        _save_session_project(flow_path, requested)
        return requested

    session = _load_session_data(flow_path)
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
        _save_session_project(flow_path, slug)
        return slug

    if len(projects) == 1:
        slug = next(iter(projects))
        _save_session_project(flow_path, slug)
        return slug

    console.print(Panel("Select a project:", title="Projects", border_style="cyan"))
    for slug, meta in projects.items():
        console.print(f" - {slug} ({meta.get('path', 'unknown')})")
    slug = typer.prompt("Project slug")
    if slug not in projects:
        console.print(Panel(f"Unknown project '{slug}'.", border_style="red"))
        raise typer.Exit(1)
    _save_session_project(flow_path, slug)
    return slug


def _resolve_change(
    flow_path: Path,
    project_slug: str,
    change_id: Optional[str],
    allow_create: bool = False,
) -> tuple[str, Path]:
    if not change_id:
        session = _load_session_data(flow_path)
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


def _project_source_path(flow_path: Path, project_slug: str) -> Path:
    projects = _load_projects_data(flow_path)
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


def _run_tool(cmd: List[str], cwd: Path) -> str:
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


@app.command()
def version():
    """Show CLI version."""
    console.print(__version__)


@app.command()
def info(here: bool = typer.Option(True, "--here", help="Use current directory")):
    """Show installed .flow-maestro info."""
    root = _project_root(here, None)
    tdir = flow_dir(root)
    ver = read_version(tdir) or "(none)"
    m = load_manifest(tdir)
    files = len(m.get("files", [])) if m else 0
    console.print(Panel.fit(f"Project: {root}\n.flow-maestro: {tdir.exists()}\nVersion: {ver}\nFiles: {files}", title="Flow Maestro Info"))


@app.command()
def init(
    source: Optional[str] = typer.Option(
        "latest", "--source", help="Release source: 'latest' (default), a tag (vX.Y.Z), or full asset URL"
    ),
    here: bool = typer.Option(True, "--here", help="Install into current directory"),
    force: bool = typer.Option(False, "--force", help="Skip confirmations and overwrite"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing"),
    preserve_local: bool = typer.Option(False, "--preserve-local", help="Keep local files, write .new beside"),
    github_token: Optional[str] = typer.Option(None, "--github-token", help="GitHub token (or GH_TOKEN/GITHUB_TOKEN)"),
    skip_tls: bool = typer.Option(False, "--skip-tls", help="Skip TLS verification (not recommended)"),
):
    """Install or update .flow-maestro from GitHub Release asset."""
    root = _project_root(here, None)
    target = flow_dir(root)
    ensure_dir(target)

    if not preserve_local:
        _purge_stage_sections(target, dry_run=dry_run)

    # Determine asset URL
    token = github_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    client = _http_client(skip_tls)

    local_asset: Optional[Path] = None
    asset_url: Optional[str] = None
    tag = "(unknown)"

    if source:
        if source.startswith("file://"):
            parsed = urlparse(source)
            local_asset = Path(parsed.path).resolve()
            tag = "(local)"
        elif Path(source).expanduser().resolve().exists():
            local_asset = Path(source).expanduser().resolve()
            tag = "(local)"
        elif source.startswith("http"):
            asset_url = source
            tag = "(direct)"
        else:
            url = _release_api_url(source)
            try:
                r = client.get(url, headers=_auth_headers(token), follow_redirects=True)
                r.raise_for_status()
            except Exception as e:
                console.print(Panel(str(e), title="Failed to fetch release info", border_style="red"))
                raise typer.Exit(1)
            rel = r.json()
            tag = rel.get("tag_name", "(unknown)")
            asset = _pick_asset(rel, ASSET_NAME)
            if not asset:
                console.print(Panel(f"Asset '{ASSET_NAME}' not found in release {tag}", title="Asset Missing", border_style="red"))
                raise typer.Exit(1)
            asset_url = asset.get("browser_download_url")
    else:
        url = _release_api_url(source)
        try:
            r = client.get(url, headers=_auth_headers(token), follow_redirects=True)
            r.raise_for_status()
        except Exception as e:
            console.print(Panel(str(e), title="Failed to fetch release info", border_style="red"))
            raise typer.Exit(1)
        rel = r.json()
        tag = rel.get("tag_name", "(unknown)")
        asset = _pick_asset(rel, ASSET_NAME)
        if not asset:
            console.print(Panel(f"Asset '{ASSET_NAME}' not found in release {tag}", title="Asset Missing", border_style="red"))
            raise typer.Exit(1)
        asset_url = asset.get("browser_download_url")

    if local_asset and not local_asset.exists():
        console.print(Panel(f"Local asset not found: {local_asset}", border_style="red"))
        raise typer.Exit(1)

    if not local_asset and not asset_url:
        console.print(Panel("Unable to resolve asset for installation.", border_style="red"))
        raise typer.Exit(1)

    # Download to temp
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / ASSET_NAME
        if local_asset:
            shutil.copy2(local_asset, zpath)
            asset_url = local_asset.as_uri()
        else:
            try:
                _download_asset(asset_url, client, token, zpath)
            except Exception as e:
                console.print(Panel(str(e), title="Download failed", border_style="red"))
                raise typer.Exit(1)

        # Extract to temp folder then merge
        content_dir = Path(td) / "content"
        extract_zip_to_dir(zpath, content_dir)
        report = merge_tree(content_dir, target, dry_run=dry_run, preserve_local=preserve_local, force=force)

    if dry_run:
        console.print(Panel(f"Dry run complete. Added: {len(report.added)}, Overwritten: {len(report.overwritten)}, Preserved: {len(report.conflicts_preserved)}", title="Dry Run"))
        raise typer.Exit(0)

    # Write metadata
    write_version(target, tag)
    manifest = compute_manifest(target, version=tag, asset_url=asset_url)
    save_manifest(target, manifest)
    ensure_readme(target)

    console.print(Panel(f"Installed Flow Maestro {tag} to {target}\nAdded: {len(report.added)} | Overwritten: {len(report.overwritten)} | Preserved: {len(report.conflicts_preserved)}", title="Success", border_style="green"))


@projects_app.command("list")
def projects_list():
    """List registered projects."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    projects = _load_projects_data(flow_path)
    if not projects:
        console.print(Panel("No projects registered.", border_style="yellow"))
        return
    lines = []
    for slug, meta in list_projects(flow_path):
        lines.append(f"{slug} - {meta.get('path', 'unknown')}")
    console.print(Panel("\n".join(lines), title="Projects", border_style="green"))


@projects_app.command("add")
def projects_add(
    slug: str = typer.Argument(..., help="Project identifier (kebab-case recommended)"),
    path: Path = typer.Option(Path("."), "--path", help="Path to project root"),
    name: Optional[str] = typer.Option(None, "--name", help="Friendly project name"),
):
    """Register a project path for Flow Maestro state."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    projects = _load_projects_data(flow_path)
    if slug in projects:
        console.print(Panel(f"Project '{slug}' already exists.", border_style="red"))
        raise typer.Exit(1)
    base = flow_path.parent
    base = flow_path.parent
    abs_path = (base / path).resolve() if not path.is_absolute() else path.resolve()
    projects[slug] = {
        "name": name or slug.replace("-", " ").title(),
        "path": str(abs_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_projects(flow_path, projects)
    ensure_dir(project_dir(flow_path, slug))
    ensure_dir(project_dir(flow_path, slug) / "changes")
    ensure_dir(project_dir(flow_path, slug) / "changes" / "archive")
    ensure_dir(project_dir(flow_path, slug) / "specs")
    _save_session_project(flow_path, slug)
    console.print(Panel(f"Registered project '{slug}' ({abs_path})", border_style="green"))


@projects_app.command("use")
def projects_use(slug: Optional[str] = typer.Argument(None, help="Project slug to activate")):
    """Select the active project for subsequent commands."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    resolved = _resolve_project(flow_path, slug)
    console.print(Panel(f"Active project: {resolved}", border_style="green"))


@changes_app.command("list")
def changes_list(
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
):
    """List active changes for a project."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
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
):
    """Create a new change workspace with scaffolds."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
    _, change_path = _resolve_change(flow_path, project_slug, change_id, allow_create=True)

    spec_created = _write_if_missing(
        change_path / "spec.md",
        SPEC_TEMPLATE.replace("{change_id}", change_id),
    )
    plan_created = _write_if_missing(
        change_path / "plan.md",
        PLAN_TEMPLATE,
    )
    tasks_created = _write_if_missing(
        change_path / "tasks.md",
        TASKS_TEMPLATE,
    )
    _write_if_missing(change_path / "qa.md", "")
    _write_if_missing(change_path / "timeline.jsonl", "")

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
        _write_if_missing(delta_path, delta_template)

    _save_session_change(flow_path, project_slug, change_id)
    _append_timeline(change_path, "changes.init", "Initialized change workspace")

    created_assets = [
        name
        for flag, name in zip(
            [spec_created, plan_created, tasks_created],
            ["spec.md", "plan.md", "tasks.md"],
        )
        if flag
    ]
    summary = ", ".join(created_assets) if created_assets else "Existing files preserved"
    console.print(Panel(f"Change '{change_id}' ready in project '{project_slug}'.\n{summary}", border_style="green"))


@changes_app.command("show")
def changes_show(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
):
    """Show paths for a change."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
    if not change_id:
        session = _load_session_data(flow_path)
        change_id = session.get("change")
    if not change_id:
        console.print(Panel("No change specified or active.", border_style="red"))
        raise typer.Exit(1)
    change_path = ensure_change_structure(flow_path, project_slug, change_id)
    spec_paths = change_delta_specs(flow_path, project_slug, change_id)
    info_lines = [f"Change path: {change_path}"]
    if spec_paths:
        info_lines.append("Delta specs:")
        info_lines.extend([f" - {cap}: {path}" for cap, path in spec_paths])
    else:
        info_lines.append("No delta specs yet.")
    console.print(Panel("\n".join(info_lines), title=f"Change - {change_id}", border_style="green"))


@research_app.command("capture")
def research_capture(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    query: List[str] = typer.Option([], "--query", "-q", help="Repeat for each ripgrep pattern to capture"),
    commits: int = typer.Option(5, "--commits", "-c", min=0, help="Number of recent commits to record"),
):
    """Append git and code-search context to notes/research.md."""

    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
    change_slug, change_path = _resolve_change(flow_path, project_slug, change_id)
    source_path = _project_source_path(flow_path, project_slug)
    if not source_path.exists():
        console.print(
            Panel(f"Project path does not exist: {source_path}", border_style="red")
        )
        raise typer.Exit(1)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections: List[str] = [f"## Snapshot - {timestamp}", ""]

    if commits:
        git_log = _run_tool(
            ["git", "log", f"-{commits}", "--pretty=format:%h %ad %s", "--date=short"],
            source_path,
        )
        if git_log:
            sections.append("### Recent Commits")
            sections.append("")
            for line in git_log.splitlines():
                stripped = line.strip()
                if stripped:
                    sections.append(f"- {stripped}")
            sections.append("")

    git_status = _run_tool(["git", "status", "-sb"], source_path)
    if git_status:
        sections.append("### Git Status")
        sections.append("")
        sections.append("```\n" + git_status + "\n```")
        sections.append("")

    for pattern in query:
        rg_output = _run_tool(
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

    _save_session_change(flow_path, project_slug, change_slug, stage="plan")
    query_count = len(query)
    plural = "query" if query_count == 1 else "queries"
    _append_timeline(
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


@quality_app.command("check")
def quality_check(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    include: List[str] = typer.Option([], "--include", "-i", help="Files to lint: spec, plan, tasks"),
):
    """Detect unresolved placeholders in change artifacts."""

    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
    change_slug, change_path = _resolve_change(flow_path, project_slug, change_id)

    targets = {
        "spec": change_path / "spec.md",
        "plan": change_path / "plan.md",
        "tasks": change_path / "tasks.md",
    }
    requested = [item.lower() for item in include if item]
    target_keys = requested or list(targets.keys())
    unknown = sorted(set(target_keys) - set(targets))
    if unknown:
        console.print(Panel(f"Unknown target(s): {', '.join(unknown)}", border_style="red"))
        raise typer.Exit(1)

    issues: List[str] = []
    for key in target_keys:
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
    _append_timeline(change_path, "quality.check", f"Quality check {status}")

    if issues:
        console.print(
            Panel(
                "\n".join(issues),
                title=f"Quality warnings - {change_slug}",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    console.print(Panel(f"No placeholder markers detected for {', '.join(target_keys)}", border_style="green"))


@timeline_app.command("show")
def timeline_show(
    change_id: Optional[str] = typer.Argument(None, help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    limit: int = typer.Option(0, "--limit", "-n", help="Show only the most recent N entries"),
):
    """Display the timeline.jsonl entries for a change."""

    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
    change_slug, change_path = _resolve_change(flow_path, project_slug, change_id)

    timeline_path = change_path / "timeline.jsonl"
    if not timeline_path.exists():
        console.print(Panel(f"No timeline found at {timeline_path}", border_style="yellow"))
        return

    events: List[dict] = []
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
    console.print(
        Panel("\n".join(lines), title=f"Timeline - {change_slug}", border_style="green")
    )


@timeline_app.command("log")
def timeline_log(
    summary: str = typer.Argument(..., help="Summary to append"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
    change_id: Optional[str] = typer.Option(None, "--change", "-c", help="Change identifier"),
    command: str = typer.Option("timeline.log", "--command", "-m", help="Command label to record"),
):
    """Append a custom entry to timeline.jsonl."""

    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
    change_slug, change_path = _resolve_change(flow_path, project_slug, change_id)

    _append_timeline(change_path, command, summary)
    console.print(
        Panel(
            f"Timeline updated for {change_slug}: {summary}",
            title="Timeline",
            border_style="green",
        )
    )


@specs_app.command("validate")
def specs_validate(
    change_id: str = typer.Argument(..., help="Change identifier"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project slug"),
):
    """Validate delta specs for a change."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
    deltas = change_delta_specs(flow_path, project_slug, change_id)
    if not deltas:
        console.print(Panel("No delta specs to validate.", border_style="yellow"))
        raise typer.Exit(1)
    errors: List[str] = []
    for capability, path in deltas:
        text = path.read_text(encoding="utf-8")
        try:
            parsed = parse_delta_markdown(text)
        except StateError as exc:
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
):
    """Apply delta specs to canonical specs and archive the change."""
    flow_path = _locate_flow_dir()
    _require_flow_dir(flow_path)
    project_slug = _resolve_project(flow_path, project)
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
    _append_timeline(change_path, "specs.apply", "Applied delta specs to canonical specs")
    archive_change(flow_path, project_slug, change_id)
    console.print(Panel(f"Applied {len(results)} spec(s) and archived change '{change_id}'", border_style="green"))


def _purge_stage_sections(target: Path, *, dry_run: bool) -> None:
    stage_dirs = [target / "commands", target / "protocols"]
    removed = []
    for stage_dir in stage_dirs:
        if stage_dir.exists() and stage_dir.is_dir():
            removed.append(stage_dir)
            if not dry_run:
                shutil.rmtree(stage_dir)
    if removed:
        verb = "Would remove" if dry_run else "Removed"
        message = f"{verb} stale stage directories:\n" + "\n".join(str(p) for p in removed)
        console.print(Panel(message, title="Purged Old Assets", border_style="yellow"))


@app.command()
def update(
    here: bool = typer.Option(True, "--here", help="Use current directory"),
    force: bool = typer.Option(False, "--force", help="Force update even if up-to-date"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes"),
    preserve_local: bool = typer.Option(False, "--preserve-local", help="Keep local changes and write .new"),
    github_token: Optional[str] = typer.Option(None, "--github-token", help="GitHub token (or GH_TOKEN/GITHUB_TOKEN)"),
    skip_tls: bool = typer.Option(False, "--skip-tls", help="Skip TLS verification"),
):
    """Update .flow-maestro to the latest release conservatively."""
    root = _project_root(here, None)
    tdir = flow_dir(root)
    current = read_version(tdir)

    # Fetch latest tag
    token = github_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    client = _http_client(skip_tls)
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
    try:
        r = client.get(url, headers=_auth_headers(token), follow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        console.print(Panel(str(e), title="Failed to fetch latest release", border_style="red"))
        raise typer.Exit(1)
    latest = r.json().get("tag_name")
    if latest and current and latest == current and not force and not dry_run:
        console.print(Panel(f"Already up-to-date ({latest})", title="No Update", border_style="green"))
        raise typer.Exit(0)

    # Delegate to init with source=latest
    init(
        source="latest",
        here=here,
        force=force,
        dry_run=dry_run,
        preserve_local=preserve_local,
        github_token=github_token,
        skip_tls=skip_tls,
    )


@app.command()
def link(
    here: bool = typer.Option(True, "--here", help="Use current directory"),
    scripts: str = typer.Option(None, "--scripts", help="sh|ps|both (default auto by OS)"),
    into: Path = typer.Option(None, "--into", help="Destination dir (default .flow-maestro/bin)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing wrappers"),
):
    """Create project-local wrapper scripts in .flow-maestro/bin that delegate to global flowm."""
    root = _project_root(here, None)
    tdir = flow_dir(root)
    bindir = into or (tdir / "bin")
    ensure_dir(bindir)

    # Decide which wrappers to create
    if not scripts:
        scripts = "ps" if os.name == "nt" else "sh"

    created = []
    if scripts in ("sh", "both"):
        sh_path = bindir / "flowm"
        if force or not sh_path.exists():
            sh_path.write_text("#!/usr/bin/env bash\nexec flowm \"$@\"\n")
            os.chmod(sh_path, 0o755)
            created.append(str(sh_path))
    if scripts in ("ps", "both"):
        ps1 = bindir / "flowm.ps1"
        cmd = bindir / "flowm.cmd"
        if force or not ps1.exists():
            ps1.write_text("#!/usr/bin/env pwsh\n& flowm $args\n")
            created.append(str(ps1))
        if force or not cmd.exists():
            cmd.write_text("@echo off\r\nflowm %*\r\n")
            created.append(str(cmd))

    console.print(Panel("\n".join(created) or "No wrappers created", title="link"))


def main():  # entry point
    app()


if __name__ == "__main__":
    main()
