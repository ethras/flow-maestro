---
description: Execute plan tasks and keep progress journals
argument-hint: {"change_id":"<slug>","project":"<slug>"}
---

# `/work` — Stage 3: Execute & Record

`/work` drives implementation. Use it to track progress against `tasks.md` (including sub-bullets), capture notes, and keep delta specs aligned with reality.

## Objectives

1. Complete tasks in order, marking them in `tasks.md`.
2. Maintain a running journal inside `notes/` or `assets/` for context.
3. Update delta specs with any behavior changes discovered during build.

## Workflow

1. **Prep**
   - Select the active project/change (`flowm projects use`, `flowm changes show`).
   - Review `plan.md` and `tasks.md` for sequencing.

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
   - Record a `work` event in `timeline.jsonl` summarizing progress and next steps.

## Validation Checklist

- [ ] Journal updated with date/time and key decisions
- [ ] `tasks.md` reflects actual status with updated sub-bullets
- [ ] Delta specs match implemented behavior
- [ ] New risks or follow-ups captured in `plan.md`
- [ ] Timeline updated with latest summary

**Next**: `/qa` once implementation stabilizes and verification can run.
