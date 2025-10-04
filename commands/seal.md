---
description: Close out an issue after gates, review, and ledger reconciliation
argument-hint: {"issue":{"id":"<issue-id>"},"summary":"...","autopost":true}
---

# `/seal` — Stage 6: Mission Closure

Invoke `/seal` when implementation, verification, and review are complete. This stage finalizes Phase IV and prepares handoff materials.

> **Autopost default**: `/seal` must publish the final summary to Linear unless explicitly run with `autopost=false` for rehearsal.

## Workflow

1. **Pre-Seal Checklist**
   - [ ] Success criteria satisfied
   - [ ] Quality gates (lint/test/build) passed or documented overrides
   - [ ] Review findings resolved; no 🔴 items remain
   - [ ] Evidence Ledger reconciled (UNKNOWN items assigned or converted to follow-up issues)
   - [ ] Progress log posted within last 24 hours
   - [ ] For parents: All children terminal with completion summaries

2. **Compose Final Summary**
   - Use the completion skeleton in `protocols/shared-templates.md`.
   - Reference Mission Decode objectives, verification results, and residual risks.

3. **Autopost Final Summary**
   - Confirm session with `get_user_linear(query: "me")` if needed.
   - Render comment via `uv run python scripts/autopost.py seal-summary --set issue_key=FM-123 --set timestamp=...` (templates in `templates/linear-macros/`).
   - `create_comment_linear(issueId: "<issue-id>", body: "<summary>")` immediately; record the posted timestamp in the Evidence Ledger.
   - On failure, set `cursor.pending_post = true`, halt state changes, and re-run `/seal` once posted.

4. **Update Issue State**
   - `update_issue_linear(id: "<issue-id>", state: "Review" or "Done")` per team conventions.

5. **Clear Cursor**
   - Write null to `.flow-maestro/cursor.json` and ensure `pending_post` is false.
   - In read-only environments, explicitly note "cursor pending (read-only env); autopost required" and stop.

## Output Skeleton

```markdown
## Final Completion Summary

**Implemented**:
- …

**Evidence Ledger Closure**:
- Observation: … (`src/...:line`)
- Risk: … → Follow-up FM-200
- UNKNOWN: None — ledger clear

**Verification**:
- Lint: PASS
- Test: PASS (15 new tests)
- Build: PASS
- Manual QA: Token generation/validation tested

**Confidence**: 100% (6/6 criteria)

**Artifacts**:
- PR: #456
- Commits: abc123, def456

**Risks & Follow-ups**:
- Token rotation strategy tracked in FM-201

**Handoff**: Ready for production deployment

**Next**: `/blueprint` (spawn follow-ups) or `/ideate` (new mission)
```

## Parent Aggregation

- Summarize child completion timestamps, quality gate outcomes, and references.
- Confirm no child remains non-terminal before updating parent state.

## Validation Checklist

- [ ] Final summary autoposted with ledger closure (or `pending_post` set w/ blocker noted)
- [ ] State updated in Linear
- [ ] Cursor cleared (pending flags removed)
- [ ] Follow-up items tracked

**Next**: Return to `/ideate` for new missions or `/blueprint` for follow-on tasks.
