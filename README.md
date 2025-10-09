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

- Copies Flow Maestro content into `.flow-maestro/` (commands, protocols, templates)
- Maintains `VERSION` and `MANIFEST.json`
- Conservative updates: backups on overwrite; `--preserve-local` writes `.new` beside files
- Supports `--dry-run`, `--force`, `--github-token`, `--skip-tls`

## Workflow Overview

Flow Maestro now mirrors OpenSpec’s simple loop — `/ideate → /plan → /work → /qa` — with state stored under `.flow-maestro/projects/<project>/changes/<change-id>/`.

| Stage | Command   | Purpose |
|-------|-----------|---------|
| 1     | `/ideate` | Capture the problem, constraints, and success signals in `spec.md`. |
| 2     | `/plan`   | Produce `plan.md`, `tasks.md`, and delta spec skeletons. |
| 3     | `/work`   | Execute tasks, journal progress, and refresh deltas. |
| 4     | `/qa`     | Verify outcomes, finalize delta specs, and prep for merge. |

Supporting CLI subcommands:

- `flowm projects add|list|use` — manage project slugs mapped to repo paths.
- `flowm changes init|list|show` — scaffold and inspect change folders.
- `flowm specs validate|apply` — lint delta specs then merge them into canonical specs.

## Release packaging

On each git tag (vX.Y.Z), the workflow builds `flow-maestro-templates.zip` containing `commands/`, `protocols/`, and `templates/` and publishes it as a Release asset.
Each release ships the updated command docs, protocols, and templates. Scripts previously tied to Linear are no longer included; publishing now happens via `flowm specs apply`.

## Notes

- Windows: wrappers use `.ps1`/`.cmd` (no symlinks). POSIX: `flowm` shell wrapper with `chmod +x`.
- For rate limits, set `GH_TOKEN` or `GITHUB_TOKEN`.
- TLS verification is on by default; `--skip-tls` is available for special cases.
- `.flow-maestro/workbench/` remains a scratchpad for research notes.
- Canonical specs live under `.flow-maestro/projects/<project>/specs/` and are updated via `flowm specs apply`.

## Release process

1. Ensure the content to ship lives under `commands/`, `protocols/`, and `templates/`.
2. Commit and push to `main`.
3. Create and push a tag (semantic):

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

4. GitHub Actions workflow "Release templates" will run and publish a Release with the asset `flow-maestro-templates.zip` (contains `commands/`, `protocols/`, `templates/`).
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
