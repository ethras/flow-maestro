# `/completion` Command

## Purpose
Complete an issue after quality gates pass. Posts completion summary and moves issue to Review/Done.

## Signature
```
/completion {"issue":{"id":"<issue-id>"},"summary":"<optional-summary>","target_state":"<optional-state>"}`
```

**Parameters**:
- `issue.id` (required): Linear issue identifier
- `summary` (optional): Brief completion summary
- `target_state` (optional): Target state name (default: "Review")

## What This Command Does

1. **Pre-Completion Verification**
   - Verifies all success criteria met
   - Checks quality gates (lint/test/build)
   - Confirms code review completed
   - Validates logging done
   - For parents: Ensures all children terminal

2. **Posts Completion Summary**
   - Formats completion note with evidence
   - Includes verification results
   - Documents risks and follow-ups
   - Links to artifacts (PRs, commits)

3. **Updates Issue Status**
   - Moves issue to "Review" (or specified state)
   - Records completion timestamp

4. **Updates State**
   - Clears cursor in `.flow-maestro/cursor.json`
   - Records completion

## Expected Output

### Child Issue Completion

```markdown
## Final Completion Summary

**Implemented**:
- JWT token generation service with RS256 algorithm
- Token validation and refresh endpoints
- Integration with existing auth middleware
- Comprehensive unit and integration tests

**Verification**:
- Lint: PASS
- Test: PASS (15 new tests, all passing)
- Build: PASS
- Manual QA: Token generation and validation tested successfully

**Code Review**:
- Completed 2024-01-15 15:00
- All 🔴 critical issues resolved
- All 🟡 warnings addressed

**Artifacts**:
- PR: #456 (merged to main)
- Commits: abc123, def456
- Tests: tests/unit/JWTService.test.ts

**Risks/Follow-ups**:
- Token rotation strategy to be implemented in FM-125
- Performance monitoring for high-volume scenarios

**Handoff**: JWT service ready for production deployment

**Posted to Linear**: FM-123 (2024-01-15 16:00)
**Status Updated**: In Progress → Review

**Recommended next command**: `/resume {"issue":{"id":"FM-100"}}` (notify parent) or `/task_creation` (create follow-ups)
```

### Parent Issue Completion

```markdown
## Final Completion Summary

**Sub-Issue Completion Status**:
- FM-101 (JWT Implementation): Completed 2024-01-15 14:30
  - Gates: Lint ✓ | Test ✓ | Build ✓
  - See FM-101 completion (2024-01-15 14:30)
- FM-102 (OAuth Integration): Completed 2024-01-15 15:45
  - Gates: Lint ⚠️ (override documented) | Test ✓ | Build ✓
  - See FM-102 completion (2024-01-15 15:45)
- FM-103 (Session Management): Completed 2024-01-15 17:00
  - Gates: Lint ✓ | Test ✓ | Build ✓
  - See FM-103 completion (2024-01-15 17:00)

**Aggregated Quality Gates**:
- Lint: 2/3 pass, 1 override (FM-102 legacy code, tracked in ISSUE-456)
- Test: 3/3 pass (57 total tests across children)
- Build: 3/3 pass

**Integration Verification**:
- Cross-component integration tests: PASS (all auth components interact correctly)
- Security review: PASS (completed 2024-01-15 17:30, no critical findings)
- Performance testing: PASS (token generation < 10ms, validation < 5ms)

**Implemented**: Complete authentication system with JWT, OAuth, and session management

**Verification**: All child quality gates satisfied, integration tests pass, security reviewed

**Handoff**: Authentication system ready for production deployment

**Posted to Linear**: FM-100 (2024-01-15 17:30)
**Status Updated**: In Progress → Review

**Recommended next command**: `/task_creation` (create deployment tasks) or done
```

## Pre-Completion Verification Checklist

**MANDATORY** - Verify before proceeding:

- [ ] All success criteria documented in Linear issue description met
- [ ] Implementation follows plan outlined in Linear issue comments
- [ ] All identified risks and impacts addressed
- [ ] Code follows existing patterns identified in context research
- [ ] No unresolved blockers or incomplete work remains

**Quality Gates**:
- [ ] Lint: PASS (or documented override)
- [ ] Test: PASS (or documented override)
- [ ] Build: PASS (or documented override)

**Documentation**:
- [ ] Code review completed (`reviews_done: true`)
- [ ] Final work log posted (`logging_done: true`)
- [ ] All decisions recorded in Linear

## Sub-Issue Completion Sequencing (Parents)

**CRITICAL**: Parent completion BLOCKED if any sub-issues non-terminal.

**Validation Checklist** (all must pass):
- [ ] Every sub-issue has `state.type` = `completed` or `canceled`
- [ ] No sub-issues remain with `state.type` = `started`, `unstarted`, etc.
- [ ] Each completed sub-issue has:
  - [ ] Final "Work Log Update" with completion timestamp
  - [ ] Quality gates passed (or documented overrides)
  - [ ] Code review completed with no unresolved 🔴 findings
  - [ ] "Final Completion Summary" posted
- [ ] Parent "Final Completion Summary" references ALL sub-issue completions

**Completion Sequencing Process**:
1. Complete each sub-issue individually first
2. Only after ALL children terminal, attempt parent completion
3. Parent summary references all child completions by identifier + timestamp

**If Blocked**:
```markdown
❌ COMPLETION BLOCKED

**Reason**: Sub-issues must be completed first

**Non-Terminal Children**:
- FM-102 (OAuth Integration) - State: In Progress

**Required Actions**:
1. Complete FM-102 individually
2. Verify FM-102 has proper completion evidence
3. Retry parent completion after FM-102 reaches terminal state

**Recommended next command**: `/startup {"issue":{"id":"FM-102"}}` (complete child first)
```

## Quality Gate Overrides

**Trigger**: A lint/test/build gate fails due to pre-existing environmental debt.

**Steps**:
1. Attempt remediation first
2. Verify failure predates your work (git history, prior CI runs)
3. Capture evidence (log excerpt, screenshot, failing command output)
4. Document override in completion summary:

```markdown
**Quality Gates**:
- Lint: ⚠️ OVERRIDE
  - Reason: Legacy lint warnings in src/legacy/OldComponent.tsx (lines 45-67)
  - Evidence: Documented in ISSUE-321, failure predates current changes (commit abc123, 2024-08-15)
  - Remediation: Scheduled in Q2 2025 refactor epic
- Test: PASS
- Build: PASS
```

**Override Rejection** occurs when:
- Reason lacks file paths, line numbers, or evidence
- No tracking issue or remediation plan cited
- Reason implies current changes introduced failure

## Existing Completion Check

Before re-completing work:

1. Verify current issue state - if already "Review" or "Done" and no new commits/comments, skip
2. Search comment history for "## Final Completion Summary"
3. Treat existing summary as current only if:
   - Posted after latest implementation work
   - Quality gates show `pass` or accepted overrides
   - Issue state reflects post-completion status
   - No additional work logs or reviews added afterwards
4. If valid summary exists, avoid duplicate; acknowledge in handoff

## Related Protocols
- `task-completion.md` - Detailed completion protocol
- `sub-issue-governance.md` - Parent completion sequencing
- `parent-child-information-flow.md` - Parent completion aggregation

## Examples

```bash
# Complete child issue
/completion {"issue":{"id":"FM-123"},"summary":"JWT service implemented and tested"}

# Complete parent issue (after all children terminal)
/completion {"issue":{"id":"FM-100"},"summary":"Authentication system complete"}

# Complete with custom target state
/completion {"issue":{"id":"FM-123"},"summary":"Feature complete","target_state":"Done"}
```

## State Updates

After `/completion`, `.flow-maestro/cursor.json` is cleared:

```json
{
  "issue_id": null,
  "mode": null,
  "last_comment_cursor": null,
  "updated_at": "2024-01-15T16:00:00Z"
}
```

