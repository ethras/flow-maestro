#!/usr/bin/env python3
"""Automate the Flow Maestro release flow."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from shutil import which

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
INIT_FILE = REPO_ROOT / "src" / "flowm_cli" / "__init__.py"
RELEASE_ASSET_NAME = "flow-maestro-templates.zip"
RELEASE_LOG = REPO_ROOT / "RELEASE_LOG.md"


def run(cmd: list[str], *, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess in the repo root."""

    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=capture_output,
        check=False,
    )
    if check and result.returncode != 0:
        if capture_output:
            sys.stderr.write(result.stderr)
        raise SystemExit(f"Command failed: {' '.join(cmd)}")
    return result


def ensure_tool(name: str) -> None:
    if which(name) is None:
        raise SystemExit(f"Required executable '{name}' not found on PATH")


def ensure_clean_git() -> None:
    status = run(["git", "status", "--porcelain"], capture_output=True)
    if status.stdout.strip():
        raise SystemExit("Git working tree is not clean; aborting release.")


def bump_version(target: str) -> str:
    content = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r"^version = \"(?P<version>[^\"]+)\"", content, re.MULTILINE)
    if not match:
        raise SystemExit("Unable to locate version in pyproject.toml")
    previous = match.group("version")
    updated = content[: match.start("version")] + target + content[match.end("version") :]
    PYPROJECT.write_text(updated, encoding="utf-8")

    init_content = INIT_FILE.read_text(encoding="utf-8")
    init_updated = re.sub(r"__version__\s*=\s*\"[^\"]+\"", f'__version__ = "{target}"', init_content)
    INIT_FILE.write_text(init_updated, encoding="utf-8")

    return previous


def run_tests(skip: bool) -> None:
    if skip:
        print("[skip] tests")
        return
    run(["uv", "run", "pytest", "-q"])


def git_commit_and_tag(version: str, skip_push: bool) -> None:
    run(["git", "add", "pyproject.toml", "src/flowm_cli/__init__.py"])
    run(["git", "commit", "-m", f"chore(release): v{version}"])
    run(["git", "tag", f"v{version}"])
    if skip_push:
        print("[skip] push/tag push")
        return
    run(["git", "pull", "--ff-only"])
    run(["git", "push"])
    run(["git", "push", "origin", f"v{version}"])


def wait_for_release(version: str, timeout: int, interval: int) -> str:
    print(f"Waiting for GitHub release v{version}...")
    deadline = time.time() + timeout
    time.sleep(min(5, interval))
    while time.time() < deadline:
        proc = run(
            [
                "gh",
                "release",
                "view",
                f"v{version}",
                "--repo",
                "ethras/flow-maestro",
                "--json",
                "assets,tagName,url",
            ],
            check=False,
            capture_output=True,
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout)
            assets = {asset.get("name"): asset.get("url") for asset in data.get("assets", [])}
            asset_url = assets.get(RELEASE_ASSET_NAME)
            if asset_url:
                print("Release is published:")
                print(f" - {RELEASE_ASSET_NAME}: {asset_url}")
                return asset_url
            print("Release found but asset not ready; retrying...")
        else:
            stderr = proc.stderr.strip()
            if "Release not found" in stderr:
                print("Release not yet available; retrying...")
            elif stderr:
                sys.stderr.write(stderr + "\n")
        time.sleep(interval)
    raise SystemExit(f"Release v{version} not visible after {timeout} seconds")


def smoke_test_release(version: str) -> None:
    target = f"git+https://github.com/ethras/flow-maestro.git@v{version}"
    print(f"Running post-release smoke test via uvx for {target}...")
    proc = run(
        ["uvx", "--from", target, "flowm", "version"],
        check=False,
        capture_output=True,
    )
    if proc.returncode != 0:
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        raise SystemExit("Release smoke test failed.")
    reported = proc.stdout.strip()
    print(f"Smoke test CLI version: {reported}")
    if reported != version:
        raise SystemExit(f"Release smoke test mismatch: expected {version}, got {reported}")


def print_release_summary(version: str, asset_url: str) -> None:
    commit = run(["git", "rev-parse", "HEAD"], capture_output=True).stdout.strip()
    print("Release summary:")
    print(f" - version: {version}")
    print(f" - commit: {commit}")
    print(f" - asset: {asset_url}")
    append_release_log(version, asset_url, commit)


def append_release_log(version: str, asset_url: str, commit: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
    entry = (
        f"## v{version} — {timestamp}\n"
        f"- commit: {commit}\n"
        f"- asset: {asset_url}\n\n"
    )
    with RELEASE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(entry)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate Flow Maestro release flow")
    parser.add_argument("version", help="Target semantic version, e.g. 0.1.7")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running pytest")
    parser.add_argument("--skip-push", action="store_true", help="Do not push commits or tags")
    parser.add_argument("--skip-wait", action="store_true", help="Skip polling for GitHub release asset")
    parser.add_argument(
        "--wait-timeout",
        type=int,
        default=600,
        help="Seconds to wait for release asset (default: 600)",
    )
    parser.add_argument(
        "--wait-interval",
        type=int,
        default=30,
        help="Seconds between release asset checks (default: 30)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ensure_tool("uv")
    ensure_tool("uvx")
    ensure_tool("gh")
    ensure_tool("git")

    ensure_clean_git()
    previous = bump_version(args.version)
    print(f"Version bumped {previous} -> {args.version}")
    run_tests(args.skip_tests)
    git_commit_and_tag(args.version, args.skip_push)

    asset_url: str | None = None
    if not args.skip_wait and not args.skip_push:
        asset_url = wait_for_release(args.version, args.wait_timeout, args.wait_interval)

    if asset_url:
        smoke_test_release(args.version)
        print_release_summary(args.version, asset_url)

    print("Release automation complete.")


if __name__ == "__main__":
    main()
