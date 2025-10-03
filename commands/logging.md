---
description: Log work progress to Linear issue comments
argument-hint: {"issue":{"id":"<issue-id>"},"observations":{...}}
---

# `/logging` — Log Work Progress

## Linear MCP Workflow

1. **Determine Scope**: Delta (< 24h, same agent) or Full log

2. **Format Work Log**:
   - **Status**: Current work status
   - **Actions**: What was done since last log
   - **Findings**: Discoveries, issues found
   - **Blockers**: Any blockers encountered
   - **Next Steps**: Planned next actions

3. **Post to Linear**: `create_comment_linear(issueId: "<issue-id>", body: "<log>")`

4. **Parent Notification** (if needed):
   - Only for blockers or coordination needs
   - Call `create_comment_linear` on parent issue
   - Reference child issue and timestamp

5. **Update State**: Write cursor to `.flow-maestro/cursor.json`

---

## Expected Output

```markdown
## Work Log Update - 2024-01-15 14:30

**Status**: Implementation in progress

**Actions**:
- Implemented JWT token generation service
- Added RS256 signing algorithm
- Created token validation interface

**Findings**:
- Existing TokenService uses HS256, switching to RS256 for better security
- Integration point with AuthMiddleware requires interface update

**Blockers**: None

**Next Steps**:
- Implement token refresh endpoint
- Update API documentation
- Run integration tests

**Posted to Linear**: FM-123 (2024-01-15 14:30)

**Next**: `/logging` (continue) or `/code_review` (if ready)
```

---

## Parent vs Child Logging

### Child Issue Logging
- Log all implementation details on child
- Include code changes, technical decisions, quality gates
- Notify parent ONLY for blockers/coordination

### Parent Issue Logging
- Coordination updates only
- Reference child logs by ID + timestamp
- No implementation details

```markdown
## Work Log Update - 2024-01-15 16:00 (Parent)

**Coordination**:
- FM-101 completed (2024-01-15 14:30) ✓
- FM-102 blocked on OAuth endpoint (notified platform team)
- FM-103 ready to start after FM-102

**Next**: Resolve FM-102 blocker

**Posted to Linear**: FM-100 (2024-01-15 16:00)
```

---

## Parent Notification Decision

**Notify Parent When**:
- Blocker requires escalation/coordination
- Cross-child dependency discovered
- Scope change affects siblings

**Don't Notify Parent For**:
- Routine progress
- Implementation details
- Quality gate results (unless blocking)

---

## Next Command Logic

- **Work continues**: `/logging` (next session)
- **Implementation complete**: `/code_review`
- **Blockers found**: Resolve, then `/resume`
- **All done**: `/code_review` → `/completion`

---

## Reference

- **Protocols**: `protocols/sub-issue-governance.md`, `protocols/parent-child-information-flow.md`
- **Linear MCP**: `create_comment_linear`
- **Token Efficiency**: ≤600 tokens, capture details in Linear not response
