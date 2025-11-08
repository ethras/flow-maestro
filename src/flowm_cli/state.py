"""State management helpers for Flow Maestro's file-based workflow."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


STATE_DIR_NAME = "state"
PROJECTS_FILENAME = "projects.json"
SESSION_FILENAME = "session.json"
SPEC_MANIFEST_FILENAME = "specs_manifest.json"
SPEC_MERGE_REPORT_FILENAME = "specs_merge_report.json"
SPEC_INDEX_FILENAME = "spec_index.json"


class StateError(RuntimeError):
    """Raised when state operations fail."""


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateError(f"Malformed JSON: {path}") from exc


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def state_dir(flow_dir: Path) -> Path:
    return flow_dir / STATE_DIR_NAME


def projects_file(flow_dir: Path) -> Path:
    return state_dir(flow_dir) / PROJECTS_FILENAME


def session_file(flow_dir: Path) -> Path:
    return state_dir(flow_dir) / SESSION_FILENAME


def load_projects(flow_dir: Path) -> Dict[str, Dict]:
    data = _load_json(projects_file(flow_dir), {})
    if not isinstance(data, dict):
        raise StateError("projects.json must contain an object")
    return data


def save_projects(flow_dir: Path, data: Dict[str, Dict]) -> None:
    _write_json(projects_file(flow_dir), data)


def load_session(flow_dir: Path) -> Dict:
    data = _load_json(session_file(flow_dir), {})
    if not isinstance(data, dict):
        raise StateError("session.json must contain an object")
    return data


def save_session(flow_dir: Path, data: Dict) -> None:
    data = dict(data)
    data.setdefault("updated_at", datetime.now(timezone.utc).isoformat())
    _write_json(session_file(flow_dir), data)


def project_dir(flow_dir: Path, slug: str) -> Path:
    return flow_dir / "projects" / slug


def change_dir(flow_dir: Path, project: str, change_id: str) -> Path:
    return project_dir(flow_dir, project) / "changes" / change_id


def canonical_spec_path(flow_dir: Path, project: str, capability: str) -> Path:
    return project_dir(flow_dir, project) / "specs" / capability / "spec.md"


def spec_manifest_path(flow_dir: Path, project: str, change_id: str) -> Path:
    return change_dir(flow_dir, project, change_id) / SPEC_MANIFEST_FILENAME


def spec_merge_report_path(flow_dir: Path, project: str, change_id: str) -> Path:
    return change_dir(flow_dir, project, change_id) / SPEC_MERGE_REPORT_FILENAME


def project_state_dir(flow_dir: Path, project: str) -> Path:
    return project_dir(flow_dir, project) / "state"


def spec_index_path(flow_dir: Path, project: str) -> Path:
    return project_state_dir(flow_dir, project) / SPEC_INDEX_FILENAME


def change_delta_specs(flow_dir: Path, project: str, change_id: str) -> List[Tuple[str, Path]]:
    base = change_dir(flow_dir, project, change_id) / "specs"
    if not base.exists():
        return []
    specs: List[Tuple[str, Path]] = []
    for spec_path in sorted(base.rglob("spec.md")):
        rel = spec_path.relative_to(base)
        capability = rel.parent.as_posix()
        specs.append((capability, spec_path))
    return specs


def list_changes(flow_dir: Path, project: str) -> List[str]:
    changes_path = project_dir(flow_dir, project) / "changes"
    if not changes_path.exists():
        return []
    return sorted(p.name for p in changes_path.iterdir() if p.is_dir() and p.name != "archive")


def list_projects(flow_dir: Path) -> Iterable[Tuple[str, Dict]]:
    projects = load_projects(flow_dir)
    for slug, meta in sorted(projects.items()):
        yield slug, meta or {}


def ensure_change_structure(flow_dir: Path, project: str, change: str) -> Path:
    directory = change_dir(flow_dir, project, change)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "specs").mkdir(exist_ok=True)
    (directory / "assets").mkdir(exist_ok=True)
    (directory / "notes").mkdir(exist_ok=True)
    return directory


@dataclass
class RequirementDelta:
    operation: str
    title: str
    body: str


@dataclass
class RenameDelta:
    old: str
    new: str


class DeltaParseResult:
    def __init__(self) -> None:
        self.requirements: Dict[str, List[RequirementDelta]] = {
            "ADDED": [],
            "MODIFIED": [],
            "REMOVED": [],
        }
        self.renames: List[RenameDelta] = []


ALLOWED_SECTIONS = {"ADDED", "MODIFIED", "REMOVED", "RENAMED"}


def parse_delta_markdown(text: str) -> DeltaParseResult:
    lines = text.splitlines()
    current_section: Optional[str] = None
    buffer: List[str] = []
    title: Optional[str] = None
    result = DeltaParseResult()

    def flush_requirement() -> None:
        nonlocal buffer, title
        if current_section in {"ADDED", "MODIFIED", "REMOVED"} and title:
            body = "\n".join(buffer).strip()
            result.requirements[current_section].append(
                RequirementDelta(current_section, title, body)
            )
        buffer = []

    for raw in lines:
        line = raw.strip("\ufeff")
        if line.startswith("## "):
            flush_requirement()
            header = line[3:].strip()
            section_name = header.split(" ")[0]
            upper = section_name.upper()
            if upper not in ALLOWED_SECTIONS:
                raise StateError(f"Unsupported delta section '{header}'")
            current_section = upper
            title = None
            continue
        if line.startswith("### Requirement:"):
            flush_requirement()
            title = line[len("### Requirement:") :].strip()
            buffer = [line]
            continue
        if current_section == "RENAMED" and line.startswith("- FROM:"):
            old = line.split(":", 1)[1].strip().strip("`")
            buffer = [old]
            continue
        if current_section == "RENAMED" and line.startswith("- TO:"):
            if not buffer:
                raise StateError("RENAMED section missing FROM entry")
            new_val = line.split(":", 1)[1].strip().strip("`")
            result.renames.append(RenameDelta(buffer[0], new_val))
            buffer = []
            continue
        if title:
            buffer.append(raw)

    flush_requirement()
    return result


def validate_delta_result(result: DeltaParseResult) -> List[str]:
    errors: List[str] = []
    for op in ("ADDED", "MODIFIED"):
        for delta in result.requirements[op]:
            if "#### Scenario:" not in delta.body:
                errors.append(f"Requirement '{delta.title}' missing scenario in {op}")
    for delta in result.requirements["REMOVED"]:
        if not delta.title:
            errors.append("REMOVED requirement missing title")
    return errors


def _find_requirement_block(content: str, title: str) -> Tuple[int, int]:
    lines = content.splitlines()
    needle = f"### Requirement: {title}"
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == needle:
            start_idx = idx
            break
    if start_idx is None:
        raise StateError(f"Requirement '{title}' not found")
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("### Requirement:"):
            end_idx = idx
            break
    return start_idx, end_idx


def apply_deltas_to_spec(content: str, deltas: DeltaParseResult) -> str:
    if "### Requirement:" not in content:
        if "## Requirements" not in content:
            content = content.rstrip() + "\n\n## Requirements\n"
        content = content.rstrip() + "\n"

    lines = content.splitlines()
    content_str = "\n".join(lines)

    for delta in deltas.requirements["REMOVED"]:
        start, end = _find_requirement_block(content_str, delta.title)
        parts = content_str.splitlines()
        new_lines = parts[:start] + parts[end:]
        content_str = "\n".join(new_lines).strip("\n") + "\n"

    for rename in deltas.renames:
        old = rename.old.replace("`", "").strip()
        new = rename.new.replace("`", "").strip()
        parts = content_str.splitlines()
        needle = old
        repl = new
        found = False
        for idx, line in enumerate(parts):
            if needle in line:
                parts[idx] = repl
                found = True
                break
        if not found:
            raise StateError(f"Cannot rename missing requirement: {old}")
        content_str = "\n".join(parts)

    for delta in deltas.requirements["MODIFIED"]:
        start, end = _find_requirement_block(content_str, delta.title)
        parts = content_str.splitlines()
        block_lines = delta.body.splitlines()
        new_lines = parts[:start] + block_lines + parts[end:]
        content_str = "\n".join(new_lines)

    if deltas.requirements["ADDED"]:
        if not content_str.endswith("\n"):
            content_str += "\n"
        for delta in deltas.requirements["ADDED"]:
            content_str = content_str.rstrip() + "\n" + delta.body.strip("\n") + "\n"

    return content_str.rstrip() + "\n"


def default_spec_content(capability: str) -> str:
    heading = capability.replace("-", " ").replace("_", " ").title()
    return f"# {heading} Specification\n\n## Requirements\n\n"


def ensure_canonical_spec(path: Path, capability: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    base = default_spec_content(capability)
    path.write_text(base, encoding="utf-8")
    return base


def archive_change(flow_dir: Path, project: str, change_id: str) -> Path:
    src = change_dir(flow_dir, project, change_id)
    if not src.exists():
        raise StateError(f"Change '{change_id}' not found")
    archive_root = project_dir(flow_dir, project) / "changes" / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dest = archive_root / f"{stamp}-{change_id}"
    if dest.exists():
        raise StateError(f"Archive destination already exists: {dest}")
    src.rename(dest)
    return dest


def relative_to_project(project_meta: Dict, current_path: Path) -> Optional[str]:
    project_path = project_meta.get("path")
    if not project_path:
        return None
    try:
        relative = current_path.resolve().relative_to(Path(project_path).resolve())
    except Exception:
        return None
    return relative.as_posix()


_SLUG_RE = re.compile(r"[^a-z0-9._-]+")


def slugify_identifier(value: str) -> str:
    token = value.strip().lower()
    if not token:
        return "item"
    token = _SLUG_RE.sub("-", token)
    token = token.strip("-")
    return token or "item"


def load_spec_index(flow_dir: Path, project: str) -> Dict[str, Dict[str, str]]:
    path = spec_index_path(flow_dir, project)
    if not path.exists():
        return {}
    data = _load_json(path, {})
    if not isinstance(data, dict):
        raise StateError("spec_index.json must contain an object")
    return data


def save_spec_index(flow_dir: Path, project: str, data: Dict[str, Dict[str, str]]) -> None:
    path = spec_index_path(flow_dir, project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
