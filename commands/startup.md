# `/startup` Command

## Purpose
Start work on a Linear issue. Reads issue details, moves to "In Progress", and establishes context.

## Signature
```
/startup {"issue":{"id":"<issue-id>"}}
```

**Parameters**:
- `issue.id` (required): Linear issue identifier (e.g., "FM-123")

## What This Command Does

1. **Reads Issue from Linear**
   - Fetches issue title, description, labels, priority
   - Retrieves parent/child relationships
   - Loads recent comments (oldest → newest)
   - Identifies blockers and dependencies

2. **Updates Issue Status**
   - Moves issue to "In Progress" (or "Doing"/"Started" alias)
   - Records startup timestamp

3. **Establishes Context**
   - Identifies if this is a parent or child issue
   - For parent issues: enumerates all sub-issues
   - For child issues: extracts relevant parent context
   - Checks for existing Context Review Summary

4. **Updates State**
   - Saves issue ID and mode to `.flow-maestro/cursor.json`
   - Records comment cursor for delta reads

## Expected Output

```markdown
## Startup: FM-123 - [Issue Title]

**Mission**:
- [2-4 bullet summary of what needs to be done]
- [Success criteria from issue description]

**Context Status**:
- Existing Context Review Summary: [Yes/No - timestamp if exists]
- Parent Issue: [None / FM-XXX with context summary]
- Sub-Issues: [None / List of children with states]

**Unknowns/Risks**:
- [Gap 1]
- [Risk 1]

**Confidence Assessment**: [X]% ([Y]/6 criteria)
- ✅ [Criterion]: [evidence]
- ❌ [Criterion]: [gap]

**Next Actions**:
[Based on confidence score and context status]

**Recommended next command**: `/context_gathering` or `/logging` [with rationale]
```

## Parent Issue Handling

When starting a parent issue (has sub-issues):

```markdown
**Parent Issue Detected**: FM-100 has 3 sub-issues

**Sub-Issues**:
- FM-101 (JWT Implementation) - State: In Progress - Last activity: 2024-01-15
- FM-102 (OAuth Integration) - State: Todo - No activity
- FM-103 (Session Management) - State: Blocked - Waiting on platform team

**Selected for Work**: FM-102 (OAuth Integration)
**Next Action**: Call `/startup {"issue":{"id":"FM-102"}}`

**Recommended next command**: `/startup {"issue":{"id":"FM-102"}}`
```

## Child Issue Handling

When starting a child issue (has parent):

```markdown
**Parent Context** (from FM-100):
- Per parent manifest (2024-01-14 10:00): All auth components use shared AuthConfig interface
- Shared constraint: Token expiry ≤ 15 minutes per security requirements
- Integration with FM-102 (OAuth): Must provide token validation interface

**This Child's Scope**: Implement JWT token generation service
```

## Confidence Gate

Before proceeding to implementation:

**<67% confidence (≤4/6 criteria)**:
```markdown
🛑 CLARIFICATION REQUIRED - Confidence 50% (3/6 criteria)

✅ What I Know:
- Success Criteria Clarity: Issue has measurable acceptance criteria → [evidence]
- Pattern Consistency: Found similar auth patterns in src/auth/ → [evidence]

❌ What I Don't Know:
- Integration Points: No documentation of external auth service integration
- Risk Mitigation: No plan for token rotation or revocation
- Sub-Issue Alignment: Unclear which sibling handles session management
- Verification Plan: No test strategy documented

🎯 Decision Point: Cannot proceed with implementation without integration details

💡 Proposed Action: Run `/context_gathering` to research integration points

❓ Question: Should I research the codebase for integration patterns, or do you have documentation I should review?
```

**≥95% confidence (6/6 criteria)**:
```markdown
Confidence Assessment: 100% (6/6 criteria)
- ✅ Success Criteria Clarity: Measurable acceptance criteria in issue description
- ✅ Integration Points: Auth service integration documented in parent manifest
- ✅ Pattern Consistency: Similar patterns found in src/auth/jwt.service.ts
- ✅ Risk Mitigation: Token rotation plan documented in parent
- ✅ Sub-Issue Alignment: Clear scope, FM-102 handles OAuth, FM-103 handles sessions
- ✅ Verification Plan: Unit tests + integration tests documented

**Recommended next command**: `/logging` to begin implementation
```

## Related Protocols
- `task-startup.md` - Detailed startup protocol
- `sub-issue-governance.md` - Parent/child workflow rules
- `parent-child-information-flow.md` - Parent/child context flow
- `universal-agent.md` - Confidence calculation protocol

## Examples

```bash
# Start work on an issue
/startup {"issue":{"id":"FM-123"}}

# Start work on a child issue after parent enumeration
/startup {"issue":{"id":"FM-124"}}
```

## State Updates

After `/startup`, `.flow-maestro/cursor.json` is updated:

```json
{
  "issue_id": "FM-123",
  "mode": "startup",
  "last_comment_cursor": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T15:00:00Z"
}
```

