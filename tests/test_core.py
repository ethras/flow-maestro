from pathlib import Path
import io
import os
import zipfile

import importlib.util
import sys

_CORE_SPEC = importlib.util.spec_from_file_location("flowm_core", "src/flowm_cli/core.py")
assert _CORE_SPEC and _CORE_SPEC.loader
core = importlib.util.module_from_spec(_CORE_SPEC)
sys.modules["flowm_core"] = core
_CORE_SPEC.loader.exec_module(core)  # type: ignore[union-attr]


def make_zip_from_dirs(zip_path: Path, src_root: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in core.list_files(src_root):
            zf.write(p, arcname=p.relative_to(src_root).as_posix())


def test_merge_add_and_manifest(tmp_path: Path):
    # Prepare source content
    src_root = tmp_path / "src"
    os.makedirs(src_root / "commands", exist_ok=True)
    os.makedirs(src_root / "protocols", exist_ok=True)
    (src_root / "commands" / "onboarding.md").write_text("hello\n")
    (src_root / "protocols" / "guide.md").write_text("p\n")

    # Create zip
    zpath = tmp_path / "x.zip"
    make_zip_from_dirs(zpath, src_root)

    # Extract to content dir
    content_dir = tmp_path / "content"
    core.extract_zip_to_dir(zpath, content_dir)

    # Merge into target
    target = tmp_path / ".flow-maestro"
    report = core.merge_tree(content_dir, target)
    assert "commands/onboarding.md" in report.added
    assert "protocols/guide.md" in report.added

    # Manifest
    manifest = core.compute_manifest(target, version="v0.0.0", asset_url="http://example")
    assert manifest["version"] == "v0.0.0"
    paths = [f["path"] for f in manifest["files"]]
    assert "commands/onboarding.md" in paths


def test_merge_overwrite_and_preserve(tmp_path: Path):
    # Existing target with a file
    target = tmp_path / ".flow-maestro"
    os.makedirs(target / "commands", exist_ok=True)
    (target / "commands" / "file.md").write_text("old\n")

    # Incoming content with changed file
    incoming = tmp_path / "incoming"
    os.makedirs(incoming / "commands", exist_ok=True)
    (incoming / "commands" / "file.md").write_text("new\n")

    # Overwrite path when not preserve; no backups written
    r1 = core.merge_tree(incoming, target, preserve_local=False)
    assert "commands/file.md" in r1.overwritten
    assert not (target / ".backup").exists()

    # Modify target again and test preserve_local
    (target / "commands" / "file.md").write_text("local change\n")
    r2 = core.merge_tree(incoming, target, preserve_local=True)
    assert "commands/file.md" in r2.conflicts_preserved
    assert (target / "commands" / "file.md.new").exists()
