---
description: Run verification passes and prepare spec deltas for merge
argument-hint: {"change_id":"<slug>","project":"<slug>"}
---

# `/qa` — Stage 4: Quality & Sign-off

`/qa` verifies that implementation matches the plan and that delta specs describe the final behavior. Use it before calling `flowm specs apply`.

## Objectives

1. Execute automated and manual verification steps and record outcomes in `qa.md`.
2. Ensure `tasks.md` is fully checked off with no outstanding blockers.
3. Confirm delta specs match the shipped behavior and include required scenarios.

## Workflow

1. **Review State**
   - Confirm `tasks.md` items (and sub-bullets) are either completed or assigned follow-ups.
   - Re-read `plan.md` to make sure scope and risks are addressed.

2. **Verification Log**
   - Create/Update `qa.md` with sections:
     - `## Scope`
     - `## Automated Verification`
     - `## Manual Verification`
     - `## Findings`
     - `## Verdict`
   - Reference concrete commands (e.g., `uv run pytest -q`) and link to artifacts in `assets/`.

3. **Findings Triage**
   - Label findings as 🔴/🟡/🟢.
   - Document mitigations or follow-up tasks in `plan.md` or spawn new change folders as needed.

4. **Spec Audit**
   - Run `flowm specs validate <change-id>` to ensure delta structure is sound.
   - Double-check that scenarios cover success/error paths.

5. **Timeline Entry**
   - Append a `qa` event to `timeline.jsonl` stating results and next steps (apply vs. return to work).

## Output Skeleton

```markdown
# QA Review — 2025-10-09

**Scope**: Feature parity check for add-auth-provider

## Automated Verification
- `uv run pytest -q` → PASS
- `npm run lint` → PASS

## Manual Verification
- Sign-in flow exercised with new provider
- Error screens confirmed for invalid tokens

## Findings
- 🔴 None
- 🟡 None
- 🟢 Document rate-limiting expectations in README

## Verdict
✅ READY — Specs ready to apply

**Next**: `flowm specs apply add-auth-provider`
```

## Validation Checklist

- [ ] `tasks.md` updated with real status + verification notes
- [ ] `qa.md` documents verification and findings
- [ ] Delta specs validated via CLI
- [ ] Follow-ups captured (new tasks or future changes)
- [ ] Timeline updated with QA outcome

**Next**: Run `flowm specs apply <change-id>` to merge deltas and archive the change. If issues persist, return to `/work` and iterate.
