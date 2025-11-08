from __future__ import annotations

from pathlib import Path

import importlib

SPEC_MODULE = importlib.import_module("flowm_cli.specs")
STATE_MODULE = importlib.import_module("flowm_cli.state")


def _seed_change(tmp_path: Path) -> tuple[Path, str, str]:
    flow_dir = tmp_path / ".flow-maestro"
    flow_dir.mkdir()
    project = "demo"
    change = "chg-expenses"
    change_specs = (
        flow_dir / "projects" / project / "changes" / change / "specs" / "expenses"
    )
    change_specs.mkdir(parents=True)
    delta = (
        "## ADDED Requirements\n"
        "### Requirement: Capture Totals\n"
        "Requirement-ID: expenses.capture.totals\n"
        "Totals SHALL reflect all items.\n\n"
        "#### Scenario: Basic\n"
        "- **WHEN** an item is added\n"
        "- **THEN** totals update\n"
    )
    (change_specs / "spec.md").write_text(delta, encoding="utf-8")
    return flow_dir, project, change


def test_prepare_and_merge_roundtrip(tmp_path: Path) -> None:
    flow_dir, project, change = _seed_change(tmp_path)
    contexts = SPEC_MODULE._gather_capability_contexts(flow_dir, project, change)
    assert len(contexts) == 1

    spec_index = STATE_MODULE.load_spec_index(flow_dir, project)
    manifest = SPEC_MODULE._build_manifest(
        flow_dir,
        project,
        change,
        contexts,
        spec_index,
        write_diffs=True,
    )
    manifest_path = STATE_MODULE.spec_manifest_path(flow_dir, project, change)
    SPEC_MODULE._write_manifest(manifest_path, manifest)
    assert manifest_path.exists()

    diff_path = (
        flow_dir
        / "projects"
        / project
        / "changes"
        / change
        / "specs"
        / "expenses"
        / "merge.diff"
    )
    assert diff_path.exists()

    results = SPEC_MODULE._perform_merge(
        flow_dir,
        project,
        change,
        contexts,
        manifest,
        spec_index,
        dry_run=False,
    )
    assert results[0]["changed"] is True

    canonical = STATE_MODULE.canonical_spec_path(flow_dir, project, "expenses")
    assert canonical.exists()
    spec_index_data = STATE_MODULE.load_spec_index(flow_dir, project)
    assert "expenses.capture.totals" in spec_index_data
