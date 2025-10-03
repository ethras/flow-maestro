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

import os
import shlex
import sys
import tempfile
from pathlib import Path
from typing import Optional

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

APP_NAME = "flowm"
__version__ = "0.1.2"
OWNER = os.getenv("FLOWM_REPO_OWNER", "ethras")
REPO = os.getenv("FLOWM_REPO_NAME", "flow-maestro")

console = Console()
app = typer.Typer(name=APP_NAME, add_completion=False)


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

    # Determine asset URL
    token = github_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    client = _http_client(skip_tls)

    if source and source.startswith("http"):
        asset_url = source
        tag = "(unknown)"
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

    # Download to temp
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / ASSET_NAME
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
        console.print(Panel(f"Dry run complete. Added: {len(report.added)}, Overwritten: {len(report.overwritten)}, Backed up: {len(report.backed_up)}, Preserved: {len(report.conflicts_preserved)}", title="Dry Run"))
        raise typer.Exit(0)

    # Write metadata
    write_version(target, tag)
    manifest = compute_manifest(target, version=tag, asset_url=asset_url)
    save_manifest(target, manifest)
    ensure_readme(target)

    console.print(Panel(f"Installed Flow Maestro {tag} to {target}\nAdded: {len(report.added)} | Overwritten: {len(report.overwritten)} | Backed up: {len(report.backed_up)} | Preserved: {len(report.conflicts_preserved)}", title="Success", border_style="green"))


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
    init.callback(source="latest", here=here, force=force, dry_run=dry_run, preserve_local=preserve_local, github_token=github_token, skip_tls=skip_tls)  # type: ignore


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

