---
description: Complete issue after quality gates pass
argument-hint: {"issue":{"id":"<issue-id>"},"summary":"..."}
---

# `/completion` — Complete Issue

## Linear MCP Workflow

1. **Pre-Completion Verification**:
   - [ ] All success criteria met
   - [ ] Quality gates passed (lint/test/build)
   - [ ] Code review completed (`reviews_done: true`)
   - [ ] Final work log posted
   - [ ] For parents: All children terminal

2. **Post Completion Summary**: `create_comment_linear(issueId: "<issue-id>", body: "<summary>")`
   - What was implemented
   - Verification results (quality gates)
   - Code review status
   - Artifacts (PRs, commits)
   - Risks/follow-ups
   - Handoff notes

3. **Update Status**: `update_issue_linear(id: "<issue-id>", state: "Review")` or "Done"

4. **Clear State**: Write null to `.flow-maestro/cursor.json`

---

## Expected Output (Child Issue)

```markdown
## Final Completion Summary

**Implemented**:
- JWT token generation service with RS256
- Token validation and refresh endpoints
- Integration with auth middleware
- Unit and integration tests

**Verification**:
- Lint: PASS
- Test: PASS (15 new tests)
- Build: PASS
- Manual QA: Token generation/validation tested

**Code Review**:
- Completed 2024-01-15 15:00
- All 🔴 critical issues resolved
- All 🟡 warnings addressed

**Artifacts**:
- PR: #456 (merged to main)
- Commits: abc123, def456
- Tests: tests/unit/JWTService.test.ts

**Risks/Follow-ups**:
- Token rotation strategy in FM-125
- Performance monitoring for high-volume

**Handoff**: JWT service ready for production

**Posted to Linear**: FM-123 (2024-01-15 16:00)
**Status Updated**: In Progress → Review

**Next**: `/resume {"issue":{"id":"FM-100"}}` (notify parent) or `/task_creation` (follow-ups)
```

---

## Expected Output (Parent Issue)

```markdown
## Final Completion Summary

**Sub-Issue Completion**:
- FM-101 (JWT): Done (2024-01-15 14:30) - Gates: ✓✓✓
- FM-102 (OAuth): Done (2024-01-15 15:45) - Gates: ⚠️✓✓ (lint override documented)
- FM-103 (Session): Done (2024-01-15 17:00) - Gates: ✓✓✓

**Aggregated Quality Gates**:
- Lint: 2/3 pass, 1 override (FM-102 legacy code, tracked in ISSUE-456)
- Test: 3/3 pass (57 total tests)
- Build: 3/3 pass

**Integration Verification**:
- Cross-component tests: PASS
- Security review: PASS (2024-01-15 17:30)
- Performance: PASS (token gen <10ms, validation <5ms)

**Implemented**: Complete authentication system

**Handoff**: Ready for production deployment

**Posted to Linear**: FM-100 (2024-01-15 17:30)
**Status Updated**: In Progress → Review

**Next**: `/task_creation` (deployment tasks) or done
```

---

## Quality Gate Overrides

If gate fails due to pre-existing debt:

1. Attempt remediation first
2. Verify failure predates your work (git history)
3. Capture evidence
4. Document override:

```markdown
**Quality Gates**:
- Lint: ⚠️ OVERRIDE
  - Reason: Legacy warnings in src/legacy/OldComponent.tsx:45-67
  - Evidence: Documented in ISSUE-321, predates changes (commit abc123)
  - Remediation: Scheduled in Q2 2025 refactor
- Test: PASS
- Build: PASS
```

---

## Parent Completion Sequencing

**CRITICAL**: Parent BLOCKED if any children non-terminal

**Validation**:
- [ ] Every child has `state.type` = `completed` or `canceled`
- [ ] Each completed child has final completion summary
- [ ] Each child has quality gates passed (or documented overrides)
- [ ] Parent summary references ALL child completions

**If Blocked**:
```markdown
❌ COMPLETION BLOCKED

**Reason**: Sub-issues must complete first

**Non-Terminal Children**:
- FM-102 (OAuth): In Progress

**Next**: `/startup {"issue":{"id":"FM-102"}}` (complete child first)
```

---

## Confidence Assessment (Final)

```markdown
**Confidence Assessment**: 100% (6/6 criteria)
1. ✅ Success Criteria: All acceptance criteria met
2. ✅ Integration Points: Verified in integration tests
3. ✅ Pattern Consistency: Code review confirmed
4. ✅ Risk Mitigation: All risks addressed or tracked
5. ✅ Sub-Issue Alignment: All children complete (parents only)
6. ✅ Verification Plan: All quality gates passed

**Evidence**: See completion summary above
```

---

## Next Command Logic

- **Follow-up tasks needed**: `/task_creation`
- **Parent needs notification**: `/resume {"issue":{"id":"<parent-id>"}}`
- **All done**: Done (no next command)

---

## Reference

- **Protocols**: `protocols/sub-issue-governance.md`, `protocols/parent-child-information-flow.md`
- **Linear MCP**: `create_comment_linear`, `update_issue_linear`
- **State**: `.flow-maestro/cursor.json` (cleared after completion)
