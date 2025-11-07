"""Root commands for installing and updating Flow Maestro assets."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import typer
from rich.panel import Panel

from .constants import APP_NAME, OWNER, REPO
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
    write_version,
)
from .utils import (
    auth_headers,
    console,
    download_asset,
    http_client,
    pick_asset,
    project_root,
    release_api_url,
)


def register_install_commands(app: typer.Typer, version_str: str) -> None:
    """Attach root commands (version/info/init/update/link) to the Typer app."""

    @app.command("version")
    def cmd_version() -> None:
        console.print(version_str)

    @app.command("info")
    def cmd_info(here: bool = typer.Option(True, "--here", help="Use current directory")) -> None:
        root = project_root(here, None)
        tdir = flow_dir(root)
        ver = read_version(tdir) or "(none)"
        manifest = load_manifest(tdir) if tdir.exists() else {"files": []}
        files = len(manifest.get("files", []))
        console.print(
            Panel.fit(
                f"Project: {root}\n.flow-maestro: {tdir.exists()}\nVersion: {ver}\nFiles: {files}",
                title="Flow Maestro Info",
            )
        )

    @app.command("init")
    def cmd_init(
        source: Optional[str] = typer.Option(
            "latest",
            "--source",
            help="Release source: 'latest' (default), a tag (vX.Y.Z), file://, or direct asset URL",
        ),
        here: bool = typer.Option(True, "--here", help="Install into current directory"),
        force: bool = typer.Option(False, "--force", help="Skip confirmations and overwrite"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without writing"),
        preserve_local: bool = typer.Option(False, "--preserve-local", help="Keep local files, write .new beside"),
        github_token: Optional[str] = typer.Option(None, "--github-token", help="GitHub token (or GH_TOKEN/GITHUB_TOKEN)"),
        skip_tls: bool = typer.Option(False, "--skip-tls", help="Skip TLS verification (not recommended)"),
    ) -> None:
        root = project_root(here, None)
        target = flow_dir(root)
        ensure_dir(target)

        if not preserve_local:
            _purge_stage_sections(target, dry_run=dry_run)

        token = github_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        client = http_client(skip_tls)
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
                url = release_api_url(source)
                try:
                    response = client.get(url, headers=auth_headers(token), follow_redirects=True)
                    response.raise_for_status()
                except Exception as exc:
                    console.print(Panel(str(exc), title="Failed to fetch release info", border_style="red"))
                    raise typer.Exit(1)
                release_data = response.json()
                tag = release_data.get("tag_name", "(unknown)")
                asset = pick_asset(release_data, ASSET_NAME)
                if not asset:
                    console.print(
                        Panel(f"Asset '{ASSET_NAME}' not found in release {tag}", title="Asset Missing", border_style="red")
                    )
                    raise typer.Exit(1)
                asset_url = asset.get("browser_download_url")
        else:
            url = release_api_url(source)
            try:
                response = client.get(url, headers=auth_headers(token), follow_redirects=True)
                response.raise_for_status()
            except Exception as exc:
                console.print(Panel(str(exc), title="Failed to fetch release info", border_style="red"))
                raise typer.Exit(1)
            release_data = response.json()
            tag = release_data.get("tag_name", "(unknown)")
            asset = pick_asset(release_data, ASSET_NAME)
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

        with tempfile.TemporaryDirectory() as tmpdir:
            zpath = Path(tmpdir) / ASSET_NAME
            if local_asset:
                shutil.copy2(local_asset, zpath)
                asset_url = local_asset.as_uri()
            else:
                try:
                    download_asset(asset_url, client, token, zpath)
                except Exception as exc:
                    console.print(Panel(str(exc), title="Download failed", border_style="red"))
                    raise typer.Exit(1)

            content_dir = Path(tmpdir) / "content"
            extract_zip_to_dir(zpath, content_dir)
            report = merge_tree(
                content_dir,
                target,
                dry_run=dry_run,
                preserve_local=preserve_local,
                force=force,
            )

        if dry_run:
            console.print(
                Panel(
                    f"Dry run complete. Added: {len(report.added)}, Overwritten: {len(report.overwritten)}, Preserved: {len(report.conflicts_preserved)}",
                    title="Dry Run",
                )
            )
            raise typer.Exit(0)

        write_version(target, tag)
        manifest = compute_manifest(target, version=tag, asset_url=asset_url)
        ensure_readme(target)
        console.print(
            Panel(
                f"Installed Flow Maestro {tag} to {target}\nAdded: {len(report.added)} | Overwritten: {len(report.overwritten)} | Preserved: {len(report.conflicts_preserved)}",
                title="Success",
                border_style="green",
            )
        )

    @app.command("update")
    def cmd_update(
        here: bool = typer.Option(True, "--here", help="Use current directory"),
        force: bool = typer.Option(False, "--force", help="Force update even if up-to-date"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes"),
        preserve_local: bool = typer.Option(False, "--preserve-local", help="Keep local changes and write .new"),
        github_token: Optional[str] = typer.Option(None, "--github-token", help="GitHub token (or GH_TOKEN/GITHUB_TOKEN)"),
        skip_tls: bool = typer.Option(False, "--skip-tls", help="Skip TLS verification"),
    ) -> None:
        root = project_root(here, None)
        tdir = flow_dir(root)
        current = read_version(tdir)

        token = github_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        client = http_client(skip_tls)
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/latest"
        try:
            response = client.get(url, headers=auth_headers(token), follow_redirects=True)
            response.raise_for_status()
        except Exception as exc:
            console.print(Panel(str(exc), title="Failed to fetch latest release", border_style="red"))
            raise typer.Exit(1)
        latest = response.json().get("tag_name")
        if latest and current and latest == current and not force and not dry_run:
            console.print(Panel(f"Already up-to-date ({latest})", title="No Update", border_style="green"))
            raise typer.Exit(0)

        cmd_init(
            source="latest",
            here=here,
            force=force,
            dry_run=dry_run,
            preserve_local=preserve_local,
            github_token=github_token,
            skip_tls=skip_tls,
        )

    @app.command("link")
    def cmd_link(
        here: bool = typer.Option(True, "--here", help="Use current directory"),
        scripts: str = typer.Option(None, "--scripts", help="sh|ps|both (default auto by OS)"),
        into: Path = typer.Option(None, "--into", help="Destination dir (default .flow-maestro/bin)"),
        force: bool = typer.Option(False, "--force", help="Overwrite existing wrappers"),
    ) -> None:
        root = project_root(here, None)
        tdir = flow_dir(root)
        bindir = into or (tdir / "bin")
        ensure_dir(bindir)

        desired = scripts or ("ps" if os.name == "nt" else "sh")
        created: list[str] = []
        if desired in ("sh", "both"):
            sh_path = bindir / "flowm"
            if force or not sh_path.exists():
                sh_path.write_text("#!/usr/bin/env bash\nexec flowm \"$@\"\n")
                os.chmod(sh_path, 0o755)
                created.append(str(sh_path))
        if desired in ("ps", "both"):
            ps1 = bindir / "flowm.ps1"
            cmd = bindir / "flowm.cmd"
            if force or not ps1.exists():
                ps1.write_text("#!/usr/bin/env pwsh\n& flowm $args\n")
                created.append(str(ps1))
            if force or not cmd.exists():
                cmd.write_text("@echo off\r\nflowm %*\r\n")
                created.append(str(cmd))

        console.print(Panel("\n".join(created) or "No wrappers created", title="link"))


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
