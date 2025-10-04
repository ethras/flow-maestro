---
description: Close out an issue after gates, review, and ledger reconciliation
argument-hint: {"issue":{"id":"<issue-id>"},"summary":"..."}
---

# `/seal` — Stage 6: Mission Closure

Invoke `/seal` when implementation, verification, and review are complete. This stage finalizes Phase IV and prepares handoff materials.

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

3. **Post to Linear**
   - `create_comment_linear(issueId: "<issue-id>", body: "<summary>")`
   - Include Evidence Ledger closure notes and follow-up tickets.

4. **Update Issue State**
   - `update_issue_linear(id: "<issue-id>", state: "Review" or "Done")` per team conventions.

5. **Clear Cursor**
   - Write null to `.flow-maestro/cursor.json` (or state "cursor pending (read-only env)").

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

- [ ] Final summary posted with ledger closure
- [ ] State updated in Linear
- [ ] Cursor cleared
- [ ] Follow-up items tracked

**Next**: Return to `/ideate` for new missions or `/blueprint` for follow-on tasks.

