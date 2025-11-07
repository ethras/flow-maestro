# Flow Maestro Installer (flowm)

Install and update Flow Maestro assets into any project under `.flow-maestro/` using a small Python CLI distributed via `uv`.

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
- `flowm changes init|list|show` — scaffold and inspect change folders.
- `flowm specs validate|apply` — lint delta specs then merge them into canonical specs.
- `flowm research capture` - append git history and `rg` snapshots to `notes/research.md` for the active change; run it (and any Context7/web lookups) during `/blueprint`, and again during `/work` if new questions appear.
- `flowm quality check` - flag placeholder text in `spec.md`, `plan.md`, or `tasks.md` before handing off to `/blueprint` or `/work`.
- `flowm timeline show|log` - review timeline.jsonl entries or append custom milestones.

## Release packaging

On each git tag (vX.Y.Z), the workflow builds `flow-maestro-templates.zip` containing `commands/` and `templates/` and publishes it as a Release asset.
Each release ships the updated command docs and templates. Scripts previously tied to Linear are no longer included; publishing now happens via `flowm specs apply`.

## Notes

- Windows: wrappers use `.ps1`/`.cmd` (no symlinks). POSIX: `flowm` shell wrapper with `chmod +x`.
- For rate limits, set `GH_TOKEN` or `GITHUB_TOKEN`.
- TLS verification is on by default; `--skip-tls` is available for special cases.
- `.flow-maestro/workbench/` remains a scratchpad for research notes.
- Canonical specs live under `.flow-maestro/projects/<project>/specs/` and are updated via `flowm specs apply`.
- Every project owns `.flow-maestro/projects/<project>/constitution.md`, a curated log of architecture patterns, integration contracts, operational guardrails, and recurring risks. Only reusable, validated insights belong there—reference it before `/ideate`, promote new findings during `/blueprint`, and refresh it as `/work` and `/qa` surface fresh information.

## Project Constitution

Flow Maestro relies on a “constitution” file per project to keep persistent memory:

- **Location**: `.flow-maestro/projects/<project>/constitution.md` (auto-created when you run `flowm projects add`).
- **Structure**: Sections for Core Architecture, Data & Integrations, Operational Guardrails, Risks & Mitigations, and a Watchlist. Each entry records a title, 1–2 sentence summary, `Source: changes/<id>/path:line`, and `Last verified: YYYY-MM-DD`.
- **Guardrails**: Include only information that multiple changes should know. If it’s speculative or limited to the active change, leave it in `notes/` or `plan.md` until proven.
- **Workflow hooks**: `/ideate` reviews constitution for background; `/blueprint` promotes reusable research into new entries; `/work` backfills anything discovered mid-build; `/qa` double-checks that entries remain accurate after verification.

Treat the constitution as the project’s collective memory—the leaner and better sourced it is, the faster future changes ramp up.

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
