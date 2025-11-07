---
description: Execute blueprint tasks and keep progress journals
argument-hint: {"change_id":"<slug>","project":"<slug>"}
---

# `/work` — Stage 3: Execute & Record

The `/work` alias points to this `commands/work.md` checklist; cite the file when collaborating so readers (or agents) know to open the Markdown rather than run a slash command.

`/work` drives implementation. Use it to track progress against `tasks.md` (including sub-bullets), capture notes, and keep delta specs aligned with reality.

## Objectives

1. Complete tasks in order, marking them in `tasks.md`.
2. Maintain a running journal inside `notes/` or `assets/` for context.
3. Update delta specs with any behavior changes discovered during build.

## Workflow

1. **Prep**
   - Select the active project/change (`flowm projects use`, `flowm changes show`).
   - Review `plan.md` and `tasks.md` for sequencing.
   - Skim `notes/research.md`. If the Research & Discovery section in `plan.md` or the research log is thin, run the missing investigations now (Context7 queries, `flowm research capture`, web searches) before touching code. Append every new finding to `notes/research.md` with timestamps so the rest of the phase inherits the context.

2. **Execution Journal**
   - For each working block, append to `notes/journal.md`:
     ```markdown
     ## 2025-10-09 — Session
     - Focus: …
     - Changes: `src/...`
     - Decisions: …
     - Follow-ups: …
     ```

3. **Checklist Maintenance**
   - Toggle tasks to `[x]` as they complete; update sub-bullets with actual files touched, snippets, and verification commands run.
   - Highlight blockers with `[BLOCKED]` and escalate in `plan.md` if scope shifts.

4. **Delta Refresh**
   - Keep capability deltas current. Any new requirements discovered during implementation must land in the corresponding `specs/<capability>/spec.md` file.

5. **Timeline Entry**
   - Record a `work` event using `flowm timeline log --command work "<progress + next steps>"`. Never append directly to `timeline.jsonl`.

6. **Constitution Touch-up**
   - When execution surfaces a reusable pattern, integration constraint, or recurring risk, run `flowm projects constitution record "<title>" --summary "<what we learned>" --source "<change>/<path>:<line>" --section <core|data|operations|risks|watchlist>` to append (or refresh) the entry in `.flow-maestro/projects/<project>/constitution.md`. The command stamps today’s date automatically; pass `--verified YYYY-MM-DD` when backfilling older insights and `--owner <team>` when logging watchlist items.
   - Reference the new constitution entry from your `notes/journal.md` block or `plan.md` follow-ups so reviewers can trace the origin. If an entry becomes obsolete, re-run the same command with an updated summary/source to refresh it before removing anything manually.

## Change vs Capability Handshake

- Treat the change folder as the parent artifact: it owns `spec.md`, `plan.md`, `tasks.md`, journals, and QA notes.
- Each capability delta (`specs/<capability>/spec.md`) is the child artifact describing normative behavior for a single capability; keep prose short and scenario-focused.
- As you finish a block of work, update both the journal and the affected delta so traceability stays tight. Reference files as `path:line` whenever you describe an edit.
- If multiple changes would touch the same capability, coordinate with `flowm changes list` and either sequence the work or reconcile deltas before QA.

## Validation Checklist

- [ ] Research gaps resolved (new findings logged in `notes/research.md` and linked from `plan.md`/`tasks.md`)
- [ ] Constitution updated via `flowm projects constitution record …` if reusable insights emerged (or existing entries re-verified)
- [ ] Journal updated with date/time and key decisions
- [ ] `tasks.md` reflects actual status with updated sub-bullets
- [ ] Delta specs match implemented behavior
- [ ] New risks or follow-ups captured in `plan.md`
- [ ] Timeline updated with latest summary

**Next**: `/qa` once implementation stabilizes and verification can run.
