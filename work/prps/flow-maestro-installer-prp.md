# PRP: Flow Maestro Installation and Update System (Python CLI + uv)

**Feature**: Flow Maestro installer/update mechanism via Python CLI (uv) that installs/updates `.flow-maestro` assets in any target project, exposes commands, and safely re-runs to update with conservative policies.

---

## Goal

**Feature Goal**: Provide a cross-platform installation and update system for Flow Maestro that:
- Installs Flow Maestro artifacts into `.flow-maestro/` in any target repo
- Exposes a global CLI `flowm` via uv; optionally creates project-local wrappers via `flowm link`
- Supports conservative, safe re-runs to update existing installations with backups and manifest tracking
- Fetches content from GitHub Releases at runtime (no registry required)

**Deliverable**: A Python Typer-based CLI (`flowm`) distributed via uv, a release packaging process producing `flow-maestro-templates.zip`, and documented workflows for `init`/`update`/`link` with conservative merge/backup behavior.

**Success Definition**:
- `flowm init --here` creates `.flow-maestro` with `commands/`, `protocols/`, `templates/`, `VERSION`, `MANIFEST.json`, `README.md`
- Re-running `flowm update` conservatively updates managed files, backs up modified ones, supports `--preserve-local` and `--dry-run`
- `flowm link` creates working wrappers on macOS/Linux (sh) and Windows (ps1/cmd)
- Works with `uv tool install` and `uvx`, handles GH token and TLS flags, with clear error UX

## User Persona (if applicable)

**Target User**: Developers integrating Flow Maestro into new or existing projects; CI systems automating setup.

**Use Case**: Initialize Flow Maestro docs/templates in a repository; periodically update as new releases are published; optionally create local wrappers.

**User Journey**:
1) Install CLI with uv or use `uvx`
2) Run `flowm init --here` in project root
3) Optionally run `flowm link` for local wrappers
4) Later run `flowm update` to bring latest assets

**Pain Points Addressed**:
- No manual PATH or symlink management (uv shims handle PATH; wrappers are optional)
- Safe updates without clobbering local changes
- Cross-platform (Windows/macOS/Linux) behavior

## Why

- Aligns with a proven model (github/spec-kit) while keeping Flow Maestro language-agnostic
- uv provides a cross-platform, registry-free distribution channel and PATH shims
- Runtime release asset fetch decouples CLI and content, enabling faster content iteration
- Conservative update policy reduces risk of overwriting local edits

## What

Provide the `flowm` CLI to install, update, and link Flow Maestro assets into any project using uv.

### Success Criteria
- [ ] `flowm` is installable via `uv tool install` and runnable via `uvx`
- [ ] `flowm init --here` installs required assets; re-running updates safely with backups
- [ ] `VERSION` and `MANIFEST.json` maintained accurately; `--dry-run` works
- [ ] `flowm link` creates OS-appropriate wrappers
- [ ] Clear error handling for network, permissions, missing assets, token issues

## All Needed Context

### Documentation & References (must-read)
- Spec Kit overview (install/update model): https://github.com/github/spec-kit#readme
- Spec Kit CLI entry point example: https://raw.githubusercontent.com/github/spec-kit/refs/heads/main/pyproject.toml
- Spec Kit CLI implementation (download/extract/merge patterns): https://raw.githubusercontent.com/github/spec-kit/refs/heads/main/src/specify_cli/__init__.py
- uv tools reference (install, uvx, PATH shims): https://docs.astral.sh/uv/guides/tools/

### Flow Maestro assets to install
- `commands/` (all)
- `protocols/` (all)
- `templates/` (all, including `templates/prp-templates/`)

### Context7 (for research-only reference)
```yaml
context7_config:
  libraryName: "github/spec-kit"
  topic: "CLI install & runtime release asset templating"
  tokens: 1500
```

### Current Codebase Structure (relevant parts)
```bash
.
├── commands/
├── protocols/
└── templates/
    └── prp-templates/
```

### Desired Codebase Structure (post-install in user project)
```bash
.
└── .flow-maestro/
   ├── commands/
   ├── protocols/
   ├── templates/
   ├── VERSION
   ├── MANIFEST.json
   ├── README.md
   └── bin/           # optional, via `flowm link`
```

(Repository additions for CLI & release workflow)
```bash
repo/
├── src/flowm_cli/
├── pyproject.toml
└── .github/workflows/release.yaml
```

### Known Gotchas & Quirks
- Windows: Avoid symlinks; prefer `.ps1`/`.cmd` wrappers
- POSIX: `chmod +x` for generated shell wrappers
- GitHub API limits: support `GH_TOKEN`/`GITHUB_TOKEN`
- ZIP nesting: detect single-root dir and flatten
- TLS on by default; `--skip-tls` exists but prints a strong warning

## Implementation Blueprint

### Data Models and Structure
- `MANIFEST.json` entries: `{ path, sha256, size }` for files under `.flow-maestro/`
- `VERSION`: release tag or version string
- Optional `INSTALL_METADATA.json` inside the ZIP (timestamp, generator version)

### Implementation Tasks (ordered by dependencies)
```yaml
Task 1: CREATE Python CLI skeleton (src/flowm_cli, pyproject.toml)
  - IMPLEMENT: Typer-based CLI with commands: init, update, link, info, version
  - FOLLOW pattern: Spec Kit’s specify_cli entrypoint structure
  - NAMING: Package "flowm-cli"; script "flowm"
  - DEPENDENCIES: typer, httpx, rich, platformdirs, truststore

Task 2: IMPLEMENT release asset fetch
  - IMPLEMENT: GET latest release; pick asset flow-maestro-templates.zip
  - FOLLOW pattern: specify_cli.download_template_from_github
  - DEPENDENCIES: GH_TOKEN via env/flag; TLS verify; error panels

Task 3: IMPLEMENT extraction & merge into .flow-maestro/
  - IMPLEMENT: Create target if missing; merge with overwrite prompts
  - FOLLOW pattern: Spec Kit ZIP flattening and merging
  - DEPENDENCIES: --here, --force, --dry-run flags

Task 4: IMPLEMENT conservative update policy
  - IMPLEMENT: MANIFEST.json with checksums; backup modified files to .backup/<ts>
  - FOLLOW pattern: Overwrite only managed files; --preserve-local writes .new
  - DEPENDENCIES: VERSION file write/read

Task 5: IMPLEMENT link (project-local wrappers)
  - IMPLEMENT: .flow-maestro/bin wrappers (sh on POSIX, ps1/cmd on Windows)
  - GOTCHA: Avoid symlinks on Windows; chmod +x on POSIX

Task 6: IMPLEMENT info/version commands
  - IMPLEMENT: Print installed version, asset URL, counts, last update
  - FOLLOW pattern: rich panels

Task 7: TESTS & CI release
  - IMPLEMENT: Unit/integration tests for fetch, extract, manifest, merge
  - IMPLEMENT: Release job to build and attach flow-maestro-templates.zip
```

### Implementation Patterns & Key Details
- Extract ZIP to temp; detect single nested folder and flatten
- Merge behavior:
  - If file absent: add
  - If present and unchanged: overwrite
  - If present and changed: backup then overwrite (or `.new` with `--preserve-local`)
- Backups: `.flow-maestro/.backup/<timestamp>/` with `SUMMARY.md`
- Prompts by default; `--force` for non-interactive CI
- `--dry-run`: compute adds/replaces/conflicts; print summary; no writes

### Integration Points
```yaml
RELEASE:
  - asset: "flow-maestro-templates.zip"
  - includes: "commands/, protocols/, templates/"
  - excludes: "dev-only files"

CI:
  - jobs: "build CLI wheel, build ZIP, publish GitHub Release assets"

UX:
  - docs: "README: uv install, uvx usage, examples (init/update/link)"
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)
```bash
ruff check .
ruff format --check .
pyright  # or mypy
```

### Level 2: Unit Tests
```bash
pytest -q
pytest tests/test_merge.py -q
```

### Level 3: Integration Testing
```bash
# Smoke: one-off install & update in temp dir
uvx --from git+https://github.com/<org>/flow-maestro.git flowm init --here
flowm update --dry-run
flowm link --scripts sh
```

## Final Validation Checklist

### Technical Validation
- [ ] `uv tool install` exposes `flowm`; `uvx` one-off works
- [ ] `flowm init --here` creates `.flow-maestro` with all assets
- [ ] Re-run update conservatively handles modifications with backups
- [ ] `MANIFEST.json` and `VERSION` updated accurately
- [ ] `link` creates functional wrappers per OS
- [ ] GH token use, TLS behavior, and error panels verified

### Feature Validation
- [ ] Success criteria from "What" satisfied
- [ ] Manual end-to-end in a sample repo: init → link → update → dry-run

### Code Quality Validation
- [ ] Python lint/type checks pass
- [ ] Tests pass and cover core flows
- [ ] Release ZIP contains correct directories; excludes dev-only files

---

## Anti-Patterns to Avoid
- ❌ Requiring users to manually manage PATH or symlinks
- ❌ Updating without backups or prompts
- ❌ Assuming symlink support on Windows
- ❌ Hardcoding GitHub API URLs without token support
- ❌ Coupling CLI code tightly to content (prefer release asset fetch)

## Example Commands for Users
```bash
# Install
uv tool install flowm-cli --from git+https://github.com/<org>/flow-maestro.git
flowm init --here

# One-off
uvx --from git+https://github.com/<org>/flow-maestro.git flowm init --here

# Update
flowm update --dry-run
flowm update --force

# Link wrappers
flowm link --scripts sh
```

## Release Checklist (brief)
1) Prepare release tag: `vX.Y.Z`
2) Build `flow-maestro-templates.zip` containing only: `commands/`, `protocols/`, `templates/`
3) Create GitHub Release for `vX.Y.Z`; upload the ZIP as asset named exactly `flow-maestro-templates.zip`
4) Verify release asset accessibility (download URL works without auth; or document GH_TOKEN usage)
5) Update README with install/update instructions if anything changed
6) Smoke test:
   - `uvx --from git+https://github.com/<org>/flow-maestro.git flowm init --here` in a temp repo
   - `flowm update --dry-run`
   - `flowm link --scripts sh` on POSIX and `--scripts ps` on Windows
7) Announce changes and any migration notes

