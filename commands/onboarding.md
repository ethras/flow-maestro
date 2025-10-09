---
description: Prepare Flow Maestro for the file-based workflow
argument-hint: (no arguments)
---

# `/onboarding` — Flow Maestro Setup

Use this script when a repository is adopting Flow Maestro's OpenSpec-style workflow. The goal is to install assets, register projects, and understand the simplified `/ideate → /plan → /work → /qa` loop.

---

## Step 1: Install / Update Assets

Run `flowm init` from the repository root to refresh `.flow-maestro/`. This will ensure the `commands/`, `protocols/`, and `templates/` folders match the latest release.

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

This creates `spec.md`, `plan.md`, `tasks.md`, an empty `qa.md`, and delta spec skeletons under `specs/`.

## Step 4: Command Loop

- `/ideate`: Fill `spec.md` via Q&A until confidence ≥95 %.
- `/plan`: Translate the idea into `plan.md` and populate `tasks.md`.
- `/work`: Execute tasks, capture notes, and mark progress.
- `/qa`: Summarize verification in `qa.md` before applying spec deltas.

Track progress with `flowm changes show <change-id>` and create additional deltas as needed.

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
- [ ] Command loop understood (ideate → plan → work → qa)
- [ ] Spec merge flow confirmed (`specs validate/apply`)

---

## Next Steps

Start with `/ideate` for the newly scaffolded change, or create more project slugs if the monorepo contains additional workspaces.
