from __future__ import annotations

from pathlib import Path

from flowm_cli.projects import _upsert_constitution_entry
from flowm_cli.templates import CONSTITUTION_TEMPLATE


def _write_template(path: Path, slug: str = "demo") -> None:
    path.write_text(
        CONSTITUTION_TEMPLATE.replace("{project_slug}", slug) + "\n",
        encoding="utf-8",
    )


def test_upsert_constitution_appends_entry(tmp_path):
    path = tmp_path / "constitution.md"
    _write_template(path)

    replaced = _upsert_constitution_entry(
        path,
        section_key="core",
        title="Event bus",
        summary="Route audit events through Kafka",
        source="chg-123/src/events.py:42",
        verified="2025-11-07",
        owner=None,
    )

    assert replaced is False
    content = path.read_text(encoding="utf-8")
    assert "- Title: Event bus" in content
    assert "Route audit events through Kafka" in content
    assert "Last verified: 2025-11-07" in content


def test_upsert_constitution_replaces_existing_entry(tmp_path):
    path = tmp_path / "constitution.md"
    _write_template(path)
    _upsert_constitution_entry(
        path,
        section_key="core",
        title="Event bus",
        summary="Initial summary",
        source="chg-122/src/events.py:10",
        verified="2025-11-01",
        owner=None,
    )

    replaced = _upsert_constitution_entry(
        path,
        section_key="core",
        title="Event bus",
        summary="Updated summary",
        source="chg-123/src/events.py:50",
        verified="2025-11-05",
        owner=None,
    )

    assert replaced is True
    content = path.read_text(encoding="utf-8")
    assert content.count("- Title: Event bus") == 1
    assert "Updated summary" in content
    assert "chg-123/src/events.py:50" in content
    assert "Last verified: 2025-11-05" in content


def test_upsert_watchlist_requires_owner_and_formats_entry(tmp_path):
    path = tmp_path / "constitution.md"
    _write_template(path)

    _upsert_constitution_entry(
        path,
        section_key="watchlist",
        title="Credit risk lag",
        summary="External feeds drop 15 min on failover",
        source="chg-200/notes.md",
        verified="2025-11-07",
        owner="SRE",
    )

    content = path.read_text(encoding="utf-8")
    assert "## Watchlist" in content
    assert "- Title: Credit risk lag" in content
    assert "  - Owner: SRE" in content
    assert "Last reviewed: 2025-11-07" in content
