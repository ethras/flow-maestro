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
```

## What it does

- Copies Flow Maestro content into `.flow-maestro/` (commands, protocols, templates)
- Maintains `VERSION` and `MANIFEST.json`
- Conservative updates: backups on overwrite; `--preserve-local` writes `.new` beside files
- Supports `--dry-run`, `--force`, `--github-token`, `--skip-tls`

## Release packaging

On each git tag (vX.Y.Z), the workflow builds `flow-maestro-templates.zip` containing `commands/`, `protocols/`, and `templates/` and publishes it as a Release asset.

## Notes

- Windows: wrappers use `.ps1`/`.cmd` (no symlinks). POSIX: `flowm` shell wrapper with `chmod +x`.
- For rate limits, set `GH_TOKEN` or `GITHUB_TOKEN`.
- TLS verification is on by default; `--skip-tls` is available for special cases.
