# Repository Guidelines

## Project Structure & Module Organization
Flow Maestro ships reusable assets plus a lightweight installer. Templates your teams consume live in `commands/`, `protocols/`, and `templates/`; keep release-bound work confined to those folders. The CLI source is under `src/flowm_cli/`, with `core.py` intentionally stdlib-only to simplify packaging. Shared fixtures and integration scenarios belong in `tests/`, while `work/` is a scratchpad for proposals or experiments that should not ship.

## Build, Test, and Development Commands
Use `uv` for repeatable workflows. `uv run flowm --help` exercises the Typer CLI entrypoint. Run unit tests with `uv run pytest -q`, which mirrors CI. During packaging or local installation, prefer `uv tool install flowm-cli --from .` for editable installs and `uv run python -m build` if you need an sdist/wheel. When verifying release artifacts, use `gh release view vX.Y.Z --repo ethras/flow-maestro --json assets,name,url` once tagging completes.

## Coding Style & Naming Conventions
Python targets 3.11+, uses 4-space indentation, and favors explicit imports. Modules and files stay lowercase with underscores (`flowm_cli/core.py`), while Typer commands use snake_case function names and CLI options mirror the existing verbs (`init`, `update`, `link`). Keep `core.py` dependency-free; any rich output or HTTP logic belongs in higher-level modules. When docstrings are needed, prefer concise triple-double-quoted summaries.

## Testing Guidelines
Tests rely on `pytest` with tmp_path-heavy fixtures; add new cases to `tests/` alongside realistic `.flow-maestro` layouts. Name tests `test_<feature>` and keep assertions focused on manifest output and merge reports. Run `uv run pytest --maxfail=1` before commits, and include coverage-sensitive paths such as backups and conflict handling when touching `core.merge_tree` or manifest helpers.

## Commit & Pull Request Guidelines
Follow the existing Conventional Commits style (`feat(commands): ...`, `docs: ...`, `chore(release): vX.Y.Z`). Commit only the generated assets and CLI code needed for the change; avoid bundling unrelated template experiments. PRs should link the motivating issue, explain any template-breaking changes, and include CLI transcripts or `pytest` output when behavior shifts. For releases, ensure `main` holds the desired assets, tag `vX.Y.Z`, push both branch and tag, monitor the “Release templates” workflow, then confirm the asset via GitHub CLI before announcing availability.
