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

## Release process

1. Ensure the content to ship lives under `commands/`, `protocols/`, and `templates/`.
2. Commit and push to `main`.
3. Create and push a tag (semantic):

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

4. GitHub Actions workflow "Release templates" will run and publish a Release with the asset `flow-maestro-templates.zip` (contains `commands/`, `protocols/`, `templates/`).
5. Verify the release and asset:

```bash
gh release view vX.Y.Z --repo ethras/flow-maestro --json assets,name,url
```

6. Consumers can install/update using uv:

```bash
uv tool install flowm-cli --from git+https://github.com/ethras/flow-maestro.git
# or one-off
uvx --from git+https://github.com/ethras/flow-maestro.git flowm init --here
```
