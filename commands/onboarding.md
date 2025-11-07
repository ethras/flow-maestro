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

Each `flowm projects add` run also seeds `.flow-maestro/projects/<slug>/constitution.md`. This “project memory” captures reusable architecture, integration contracts, and guardrails—treat it as required reading before deep dives and update it whenever you learn something future changes need to know.

## Step 3: Change Folders

Every initiative lives in `.flow-maestro/projects/<project>/changes/<change-id>/`. Scaffold the first change:

```bash
flowm changes init add-auth-provider --project web --capability auth
```

This creates `spec.md`, `plan.md`, `tasks.md`, an empty `qa.md`, and delta spec skeletons under `specs/`.

## Step 4: Command Loop

- `/ideate`: Fill `spec.md` via Q&A until confidence ≥95 %.
- `/blueprint`: Translate the idea into `plan.md` and populate `tasks.md`.
- `/work`: Execute tasks, capture notes, and mark progress.
- `/qa`: Summarize verification in `qa.md` before applying spec deltas.

Track progress with `flowm changes show <change-id>` and create additional deltas as needed.

### Research & Quality Helpers

- `flowm research capture --query <pattern>` collects recent git log entries, status, and `rg` snippets into `notes/research.md` for the active change.
- `flowm quality check` flags template placeholders (e.g. `<describe the gap or opportunity>`) inside `spec.md`, `plan.md`, or `tasks.md`.
- `flowm timeline show|log` lets you review or append timeline entries while you progress through `/blueprint` and `/work`.

## Strategos Prime Loop & Confidence

Flow Maestro inherits the Strategos Prime cadence—every change moves through four disciplined phases:

1. **Ideation (`/ideate`)** — Clarify the problem, users, and success signals in `spec.md`; stop only when confidence ≥95 %.
2. **Blueprint (`/blueprint`)** — Translate the spec into `plan.md`, expand `tasks.md`, and seed capability deltas.
3. **Execution (`/work`)** — Follow `tasks.md` in order, keep journals/timeline entries current, and refresh delta specs anytime behavior shifts.
4. **Quality (`/qa` + `flowm specs apply`)** — Log automated/manual verification in `qa.md`, validate deltas, then merge and archive.

**Confidence criteria** (all six must hold before applying specs):

- Success criteria and constraints are measurable inside `spec.md`.
- Dependencies are listed in `plan.md` with owners or sequencing.
- Implementation patterns live in `plan.md` plus `notes/journal.md` snapshots.
- Risks have mitigation owners; `[BLOCKED]` tasks call them out explicitly.
- Delta specs are validated and scoped to the behavior that changes.
- Verification commands (automated + manual) ran recently with reproducible evidence.

## Governance & Information Flow

### Responsibilities

- **Change folder (`changes/<id>/`)** — Owns `spec.md`, `plan.md`, `tasks.md`, journals, timeline, and QA notes.
- **Capability delta (`specs/<capability>/spec.md`)** — Narrates normative behavior deltas per capability; keep prose tight and scenario-focused.

### Flow of information

1. `/ideate` records the intent.
2. `/blueprint` decides which capabilities move and drafts deltas.
3. `/work` pushes detailed decisions into journals and deltas.
4. `/qa` verifies capability outcomes and finalizes deltas.
5. `flowm specs apply` projects those deltas into canonical specs before archiving the change.

### Coordination rules

- Do not begin `/work` until `/blueprint` lists every affected capability plus task coverage.
- Keep changes small enough to finish within a few focused sessions; spawn a new change if scope creeps.
- Reference files as `path:line` inside journals, plans, and QA notes for traceability.
- Use `flowm changes list` during standups to avoid overlapping work on the same capability.

### Quality gates & conflict handling

- `tasks.md` cannot carry unchecked blockers; if something stalls, flag it and either mitigate or cut scope.
- Journals and QA notes must cite real commands/logs—no “tests passed” placeholders.
- If two changes touch the same capability, coordinate ordering or reconcile delta files before running `specs apply`.
- After `flowm specs apply`, archive immediately; never keep mutable state in `changes/` once the spec merges.

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
