"""
Flow Maestro installer core helpers (stdlib-only).
This module avoids third-party imports so tests can run without external deps.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


ASSET_NAME = "flow-maestro-templates.zip"
MANIFEST_NAME = "MANIFEST.json"
VERSION_NAME = "VERSION"
BACKUP_DIRNAME = ".backup"


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def list_files(root: Path) -> List[Path]:
    return [p for p in root.rglob("*") if p.is_file() and not p.is_symlink()]


def relpath(path: Path, base: Path) -> str:
    return str(path.relative_to(base).as_posix())


def load_manifest(target_dir: Path) -> Dict:
    m = target_dir / MANIFEST_NAME
    if not m.exists():
        return {}
    try:
        return json.loads(m.read_text())
    except Exception:
        return {}


def save_manifest(target_dir: Path, data: Dict) -> None:
    (target_dir / MANIFEST_NAME).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_version(target_dir: Path, version: str) -> None:
    (target_dir / VERSION_NAME).write_text(version.strip() + "\n")


def read_version(target_dir: Path) -> str | None:
    f = target_dir / VERSION_NAME
    if f.exists():
        return f.read_text().strip() or None
    return None


@dataclass
class MergeReport:
    added: List[str]
    overwritten: List[str]
    backed_up: List[str]
    conflicts_preserved: List[str]


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def merge_tree(src_dir: Path, dest_dir: Path, *, dry_run: bool = False, preserve_local: bool = False, force: bool = False) -> MergeReport:
    """Merge src_dir into dest_dir conservatively.
    - If dest missing: add
    - If dest exists and different:
      - preserve_local: write .new beside existing
      - else: backup then overwrite
    Returns a MergeReport with relative paths from dest_dir.
    """
    ensure_dir(dest_dir)
    report = MergeReport(added=[], overwritten=[], backed_up=[], conflicts_preserved=[])

    # Prepare backup root per operation
    backup_root = dest_dir / BACKUP_DIRNAME / _timestamp()

    for sp in list_files(src_dir):
        rel = relpath(sp, src_dir)
        dp = dest_dir / rel
        ensure_dir(dp.parent)

        if not dp.exists():
            if not dry_run:
                shutil.copy2(sp, dp)
            report.added.append(rel)
            continue

        # Compare content
        try:
            src_hash = sha256_file(sp)
            dst_hash = sha256_file(dp)
        except Exception:
            src_hash = dst_hash = None

        if src_hash == dst_hash:
            # Same content; treat as overwrite innocuous
            if not dry_run:
                shutil.copy2(sp, dp)
            report.overwritten.append(rel)
            continue

        # Different content
        if preserve_local:
            newp = dp.with_suffix(dp.suffix + ".new")
            if not dry_run:
                shutil.copy2(sp, newp)
            report.conflicts_preserved.append(rel)
        else:
            # Backup and overwrite
            if not dry_run:
                ensure_dir(backup_root / dp.parent.relative_to(dest_dir))
                shutil.copy2(dp, backup_root / rel)
                shutil.copy2(sp, dp)
            report.backed_up.append(rel)
            report.overwritten.append(rel)

    # Write backup summary
    if (report.backed_up or report.conflicts_preserved) and not dry_run:
        ensure_dir(backup_root)
        summary = [
            f"Backups: {len(report.backed_up)}",
            *[f"B {p}" for p in sorted(report.backed_up)],
            f"Preserved (.new): {len(report.conflicts_preserved)}",
            *[f"P {p}" for p in sorted(report.conflicts_preserved)],
        ]
        (backup_root / "SUMMARY.md").write_text("\n".join(summary) + "\n")

    return report


def compute_manifest(target_dir: Path, *, version: str, asset_url: str | None) -> Dict:
    files = []
    for f in list_files(target_dir):
        if f.name in {MANIFEST_NAME, VERSION_NAME}:
            continue
        if BACKUP_DIRNAME in f.parts and BACKUP_DIRNAME in f.parents:
            # skip backup contents
            continue
        files.append({
            "path": relpath(f, target_dir),
            "sha256": sha256_file(f),
            "size": f.stat().st_size,
        })
    data = {
        "version": version,
        "asset": asset_url,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "files": sorted(files, key=lambda x: x["path"]),
    }
    return data


def zip_has_single_root(zip_ref) -> Tuple[bool, str | None]:
    """Given a ZipFile, detect single top-level folder name if present."""
    names = [n for n in zip_ref.namelist() if not n.endswith("/")]
    if not names:
        return False, None
    roots = {n.split("/", 1)[0] for n in names}
    if len(roots) == 1:
        return True, next(iter(roots))
    return False, None


def copy_tree(src: Path, dst: Path) -> None:
    for sp in list_files(src):
        rel = relpath(sp, src)
        dp = dst / rel
        ensure_dir(dp.parent)
        shutil.copy2(sp, dp)


def extract_zip_to_dir(zip_path: Path, dest_dir: Path) -> Path:
    """Extract zip into dest_dir, flattening single-root archive if needed. Returns folder containing content."""
    import zipfile

    ensure_dir(dest_dir)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
        single, root = zip_has_single_root(zf)
    if single and root:
        # move contents up
        nested = dest_dir / root
        temp_move = dest_dir / (root + "_tmp_move")
        nested.rename(temp_move)
        # copy up then remove temp
        copy_tree(temp_move, dest_dir)
        shutil.rmtree(temp_move, ignore_errors=True)
    return dest_dir


def find_project_root(cwd: Path) -> Path:
    return cwd


def flow_dir(project_root: Path) -> Path:
    return project_root / ".flow-maestro"


def ensure_readme(target_dir: Path) -> None:
    readme = target_dir / "README.md"
    if readme.exists():
        return
    readme.write_text(
        "Flow Maestro assets installed here. Do not edit generated files unless you know what you're doing.\n"
    )

