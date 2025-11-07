---
description: Prepare Flow Maestro for the file-based workflow
argument-hint: (no arguments)
---

# `/onboarding` — Flow Maestro Setup

Treat `/onboarding` as shorthand for this `commands/onboarding.md` runbook. Reference the file path when sharing steps so collaborators (and agents) read the Markdown instead of expecting a slash command to execute.

Use this script when a repository is adopting Flow Maestro's OpenSpec-style workflow. The goal is to install assets, register projects, and understand the simplified `/ideate → /blueprint → /work → /qa` loop.

---

## Step 1: Confirm Assets Are Current

If `.flow-maestro/` already exists and matches the release you expect to use, continue to Step&nbsp;2—no reinstall needed. Run `flowm init` only when setting up Flow Maestro for the first time or when you intentionally pull in updated assets.

```bash
uvx --from . flowm init --here
```

## Step 2: Register Projects

Flow Maestro stores state at the monorepo root. Register each workspace with a slug:

```bash
flowm projects add web --path apps/web
flowm projects add api --path services/api
```

Use `flowm projects list` to confirm, and `flowm projects use <slug>` to set the active project.

## Step 3: Change Folders

Every initiative lives in `.flow-maestro/projects/<project>/changes/<change-id>/`. Scaffold the first change:

```bash
flowm changes init add-auth-provider --project web --capability auth
```

This creates `spec.md`, `blueprint.md`, `tasks.md`, an empty `qa.md`, and delta spec skeletons under `specs/`.

## Step 4: Command Loop

- `/ideate`: Fill `spec.md` via Q&A until confidence ≥95 %.
- `/blueprint`: Translate the idea into `blueprint.md` and populate `tasks.md`.
- `/work`: Execute tasks, capture notes, and mark progress.
- `/qa`: Summarize verification in `qa.md` before applying spec deltas.

Track progress with `flowm changes show <change-id>` and create additional deltas as needed.

### Research & Quality Helpers

- `flowm research capture --query <pattern>` collects recent git log entries, status, and `rg` snippets into `notes/research.md` for the active change.
- `flowm quality check` flags template placeholders (e.g. `<describe the gap or opportunity>`) inside `spec.md`, `blueprint.md`, or `tasks.md`.
- `flowm timeline show|log` lets you review or append timeline entries while you progress through `/blueprint` and `/work`.

## Step 5: Apply Specs

Once QA passes, merge deltas into canonical specs and archive the change:

```bash
flowm specs validate add-auth-provider
flowm specs apply add-auth-provider
```

Canonical specs live under `.flow-maestro/projects/<project>/specs/`. After `apply`, the change moves to `changes/archive/`.

---

## Validation Checklist

- [ ] `.flow-maestro/` installed or updated
- [ ] Projects registered in `state/projects.json`
- [ ] First change folder scaffolded
- [ ] Command loop understood (ideate → blueprint → work → qa)
- [ ] Spec merge flow confirmed (`specs validate/apply`)

---

## Next Steps

Start with `/ideate` for the newly scaffolded change, or create more project slugs if the monorepo contains additional workspaces.
