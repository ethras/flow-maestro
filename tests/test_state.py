from __future__ import annotations

from pathlib import Path
import importlib.util
import sys

import pytest

_STATE_SPEC = importlib.util.spec_from_file_location("flowm_state", "src/flowm_cli/state.py")
assert _STATE_SPEC and _STATE_SPEC.loader
state = importlib.util.module_from_spec(_STATE_SPEC)
sys.modules["flowm_state"] = state
_STATE_SPEC.loader.exec_module(state)  # type: ignore[union-attr]

StateError = state.StateError
apply_deltas_to_spec = state.apply_deltas_to_spec
ensure_canonical_spec = state.ensure_canonical_spec
parse_delta_markdown = state.parse_delta_markdown
validate_delta_result = state.validate_delta_result
slugify_identifier = state.slugify_identifier
load_spec_index = state.load_spec_index
save_spec_index = state.save_spec_index
spec_index_path = state.spec_index_path


def test_apply_added_requirement(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.md"
    base = ensure_canonical_spec(spec_path, "payments")
    delta = """## ADDED Requirements
### Requirement: Payment Authorization
Transactions SHALL require authorization.

#### Scenario: Basic purchase
- **WHEN** a customer submits a purchase
- **THEN** authorization occurs
"""
    parsed = parse_delta_markdown(delta)
    assert not validate_delta_result(parsed)
    updated = apply_deltas_to_spec(base, parsed)
    assert "### Requirement: Payment Authorization" in updated
    assert "Transactions SHALL require authorization." in updated


def test_apply_modified_requirement(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.md"
    initial = (
        "# Checkout Specification\n\n## Requirements\n\n"
        "### Requirement: Cart Totals\nTotals SHALL sum all items.\n\n"
        "#### Scenario: Basic\n- **WHEN** items added\n- **THEN** totals update\n"
    )
    spec_path.write_text(initial)
    delta = """## MODIFIED Requirements
### Requirement: Cart Totals
Totals SHALL include tax.

#### Scenario: Basic
- **WHEN** items added
- **THEN** totals include tax
"""
    parsed = parse_delta_markdown(delta)
    updated = apply_deltas_to_spec(initial, parsed)
    assert "Totals SHALL include tax." in updated
    assert "Totals SHALL sum all items." not in updated


def test_parse_invalid_section_raises() -> None:
    bad_delta = "## UNKNOWN Section\n"
    with pytest.raises(StateError):
        parse_delta_markdown(bad_delta)


def test_validate_requires_scenario() -> None:
    delta = """## ADDED Requirements
### Requirement: Missing Scenario
Body without scenario
"""
    parsed = parse_delta_markdown(delta)
    errors = validate_delta_result(parsed)
    assert errors
    assert "missing scenario" in errors[0].lower()


def test_slugify_identifier_handles_symbols() -> None:
    assert slugify_identifier("Expenses Mobile!!") == "expenses-mobile"
    assert slugify_identifier("   ") == "item"


def test_spec_index_roundtrip(tmp_path: Path) -> None:
    flow_dir = tmp_path / ".flow-maestro"
    flow_dir.mkdir()
    project = "demo"
    project_root = flow_dir / "projects" / project
    project_root.mkdir(parents=True)
    data = {"req-1": {"capability": "expenses", "title": "Totals"}}
    save_spec_index(flow_dir, project, data)
    path = spec_index_path(flow_dir, project)
    assert path.exists()
    loaded = load_spec_index(flow_dir, project)
    assert loaded == data
