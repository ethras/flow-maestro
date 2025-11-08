# Flow Maestro Installer (flowm)

Install and update Flow Maestro assets into any project under `.flow-maestro/` using a small Python CLI distributed via `uv`. The CLI now exposes dedicated modules for projects, changes, specs, research, quality, timeline, installer helpers, and—new in v0.4.10—constitution management so reusable findings stay consistent across commands and documentation.

## Quick start

```bash
# Install once (recommended)
uv tool install flowm-cli --from git+https://github.com/ethras/flow-maestro.git
flowm init --here

# One-off use (no install)
uvx --from git+https://github.com/ethras/flow-maestro.git flowm init --here

# Update existing installation
flowm update --dry-run
flowm update --force

# Create project-local wrappers
flowm link --scripts sh

# Register a project and scaffold a change
flowm projects add web --path apps/web
flowm changes init add-auth-provider --project web --capability auth
flowm specs validate add-auth-provider
```

## What it does

- Copies Flow Maestro content into `.flow-maestro/` (commands and templates)
- Maintains `VERSION` and `MANIFEST.json`
- Conservative updates: backups on overwrite; `--preserve-local` writes `.new` beside files
- Supports `--dry-run`, `--force`, `--github-token`, `--skip-tls`

## Workflow Overview

Flow Maestro now mirrors OpenSpec’s simple loop — `/ideate → /blueprint → /work → /qa` — with state stored under `.flow-maestro/projects/<project>/changes/<change-id>/`. The slash names are shorthand for Markdown guides in `commands/*.md`; for example `/ideate` means “open `commands/ideate.md` and follow it.” Mention the alias when chatting, but link or quote the file so humans and agents know where to read.

| Stage | Command   | Purpose |
|-------|-----------|---------|
| 1     | `/ideate` (`commands/ideate.md`) | Capture the problem, constraints, and success signals in `spec.md`. |
| 2     | `/blueprint` (`commands/blueprint.md`)  | Produce `plan.md`, `tasks.md`, and delta spec skeletons while logging Context7/web/code research in `notes/research.md`. |
| 3     | `/work` (`commands/work.md`)  | Execute tasks, backfill any missing research, journal progress, and refresh deltas. |
| 4     | `/qa` (`commands/qa.md`)    | Verify outcomes, finalize delta specs, and prep for merge. |

Supporting CLI subcommands:

- `flowm projects add|list|use` — manage project slugs mapped to repo paths.
- `flowm projects constitution record` — append or refresh entries in `.flow-maestro/projects/<project>/constitution.md` with normalized formatting (title, summary, source, verification date, optional owner for watchlist entries). Use this instead of manual Markdown edits.
- `flowm changes init|list|show` — scaffold and inspect change folders.
- `flowm specs status|prepare|merge|validate|apply` — list pending delta specs, build manifests + diffs, merge them into canonical specs, or fall back to the original validate/apply flow when needed.
- `flowm specs rename-capability` — rename canonical + in-flight capability folders so names stay product-oriented (e.g., consolidate `expenses-mobile`, `expenses-web`, `expenses-backend` into a single `expenses`).
- `flowm research capture` - append git history and `rg` snapshots to `notes/research.md` for the active change; run it (and any Context7/web lookups) during `/blueprint`, and again during `/work` if new questions appear.
- `flowm quality check` - flag placeholder text in `spec.md`, `plan.md`, or `tasks.md` before handing off to `/blueprint` or `/work`.
- `flowm timeline show|log` - review timeline entries or append milestones; always use this command instead of editing `timeline.jsonl` manually.

## Release packaging

On each git tag (vX.Y.Z), the workflow builds `flow-maestro-templates.zip` containing `commands/` and `templates/` and publishes it as a Release asset.
Each release ships the updated command docs and templates. Scripts previously tied to Linear are no longer included; publishing now happens via `flowm specs apply`.

## Notes

- Windows: wrappers use `.ps1`/`.cmd` (no symlinks). POSIX: `flowm` shell wrapper with `chmod +x`.
- For rate limits, set `GH_TOKEN` or `GITHUB_TOKEN`.
- TLS verification is on by default; `--skip-tls` is available for special cases.
- `.flow-maestro/workbench/` remains a scratchpad for research notes.
- Canonical specs live under `.flow-maestro/projects/<project>/specs/` and are updated via `flowm specs apply`.
- Run `flowm specs prepare <change>` before `/qa` to capture `specs_manifest.json` and per-capability `merge.diff` files; agents (or reviewers) can read `specs_merge_report.json` after `flowm specs merge` to understand what changed.
- Every project owns `.flow-maestro/projects/<project>/constitution.md`, a curated log of architecture patterns, integration contracts, operational guardrails, and recurring risks. Only reusable, validated insights belong there—reference it before `/ideate`, promote new findings during `/blueprint`, and refresh it via `flowm projects constitution record` as `/work` and `/qa` surface new information.

## Project Constitution

Flow Maestro relies on a “constitution” file per project to keep persistent memory:

- **Location**: `.flow-maestro/projects/<project>/constitution.md` (auto-created when you run `flowm projects add`).
- **Structure**: Sections for Core Architecture, Data & Integrations, Operational Guardrails, Risks & Mitigations, and a Watchlist. Each entry records a title, 1–2 sentence summary, `Source: changes/<id>/path:line`, and `Last verified: YYYY-MM-DD`.
- **Guardrails**: Include only information that multiple changes should know. If it’s speculative or limited to the active change, leave it in `notes/` or `plan.md` until proven.
- **Workflow hooks**: `/ideate` reviews constitution for background; `/blueprint` promotes reusable research into new entries; `/work` backfills anything discovered mid-build; `/qa` double-checks that entries remain accurate after verification. Each stage should use `flowm projects constitution record` so entries stay normalized and dated automatically.

### Recording a finding

```bash
flowm projects constitution record "Event Bus Guardrail" \
  --summary "Route audit events through Kafka with schema v3; never bypass retries" \
  --source "chg-123/src/events.py:42" \
  --section operations \
  --project web
```

- Omitting `--verified` stamps today’s date automatically (UTC). Pass `--verified YYYY-MM-DD` when backfilling older insights.
- When `--section watchlist` is chosen, include `--owner <team>` so the entry tracks who is watching the risk.
- Re-running the command with the same title in the same section replaces the existing block (helpful for refreshing “Last verified” without editing Markdown).

### Constitution touchpoints per stage

| Stage | What to read/update | CLI helper |
|-------|---------------------|-----------|
| `/ideate` | Read existing constitution entries for context; log contradictions as research tasks. | `flowm projects constitution record` (only when you convert a research insight into a reusable guardrail). |
| `/blueprint` | Promote validated research into entries so downstream stages inherit constraints. | `flowm projects constitution record --section core|data|operations|risks|watchlist`. |
| `/work` | Backfill mid-build discoveries (integration constraints, reusable code paths) and cite them in `notes/journal.md`. | Same command; include `--source change-id/path:line` for traceability. |
| `/qa` | Refresh “Last verified” dates for anything touched and prune obsolete entries. | `flowm projects constitution record --verified <date>` when re-validating. |

Treat the constitution as the project’s collective memory—the leaner and better sourced it is, the faster future changes ramp up. Because the entry helper enforces structure, you can safely rely on automated diffs to spot what changed between releases.

### Capability naming & consolidation

- Capabilities should reflect user-facing domains (`expenses`, `billing`, `auth`) rather than channel-specific slices (`expenses-mobile`). This keeps canonical specs stable while change folders carry the platform nuance.
- If legacy projects already diverged, use `flowm specs rename-capability <old> <new>` to move canonical specs and active delta folders to the new name. Run `flowm specs prepare` afterward to refresh manifests.
- When several channel-specific folders must collapse into one, pick the target name (e.g., `expenses`), migrate/merge the Markdown content manually inside `.flow-maestro/projects/<project>/specs/<target>/spec.md`, then remove the obsolete folders via `flowm specs rename-capability`.

## Release process

1. Ensure the content to ship lives under `commands/` and `templates/`.
2. Commit and push to `main`.
3. Create and push a tag (semantic):

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

4. GitHub Actions workflow "Release templates" will run and publish a Release with the asset `flow-maestro-templates.zip` (contains `commands/` and `templates/`).
5. Verify the release and asset (automation also runs an `uvx` smoke test and appends details to `RELEASE_LOG.md`):

```bash
gh release view vX.Y.Z --repo ethras/flow-maestro --json assets,name,url
```

### Maintainer shortcut

Use `scripts/create_release.py <version>` to automate version bumps, testing, tagging, pushes, release verification, and a post-release `uvx --from ... flowm version` smoke test. The script also appends a summary entry to `RELEASE_LOG.md`. It polls GitHub every 10 seconds and times out after 120 seconds by default; pass `--skip-wait` if you only need the local updates without polling GitHub.

6. Consumers can install/update using uv:

```bash
uv tool install flowm-cli --from git+https://github.com/ethras/flow-maestro.git
# or one-off
uvx --from git+https://github.com/ethras/flow-maestro.git flowm init --here
```

### Post-release checklist

After tagging, but before announcing, run:

1. `uv tool install flowm-cli --from git+https://github.com/ethras/flow-maestro.git@vX.Y.Z --force`
2. `flowm version` (expect `X.Y.Z`).
3. Spot-check `flowm projects constitution record --help` to ensure the new helper ships as expected.
4. Re-run `uv run flowm --help` in a clean workspace to confirm Typer wiring still lists all subcommands.
