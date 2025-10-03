## Release Process

1. Verify the content to ship lives under `commands/`, `protocols/`, and `templates/`.
2. Commit the changes on `main` (include required co-author line when applicable) and push: `git push origin main`.
3. Create and push the release tag (semantic version):
   - `git tag vX.Y.Z`
   - `git push origin vX.Y.Z`
4. Wait for the “Release templates” GitHub Action to publish the release asset.
5. Validate the release with `gh release view vX.Y.Z --repo ethras/flow-maestro --json assets,name,url`.
