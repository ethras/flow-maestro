# `/resume` Command

## Purpose
Resume work on an issue. Fetches latest snapshot and comments to decide next action. Never changes status.

## Signature
```
/resume {"issue":{"id":"<issue-id>"}}
```

**Parameters**:
- `issue.id` (required): Linear issue identifier (e.g., "FM-123")

## What This Command Does

1. **Fetches Latest Snapshot**
   - Reads current issue state, priority, assignee
   - Retrieves comments since last cursor (delta read)
   - Checks for sub-issue updates
   - Identifies blockers and status changes

2. **Assesses Context Freshness**
   - Validates existing Context Review Summary
   - Checks for new decisions or risks in comments
   - Identifies scope changes or new requirements

3. **Determines Next Action**
   - Based on current state and recent activity
   - Considers confidence level for next steps
   - Recommends appropriate next command

4. **Updates State**
   - Updates comment cursor in `.flow-maestro/cursor.json`
   - Records resume timestamp

## Expected Output

```markdown
## Resume: FM-123 - [Issue Title]

**Current Status**:
- State: [In Progress / Blocked / etc.]
- Priority: [High / Medium / Low]
- Last Activity: [timestamp]
- Assignee: [name]

**Recent Activity** (since last session):
- [Comment 1 summary - timestamp]
- [Comment 2 summary - timestamp]
- [Status change or blocker update]

**Context Assessment**:
- Context Review Summary: [Current / Outdated / Missing]
- Confidence: [X]% ([Y]/6 criteria)
- Blockers: [None / List]

**Sub-Issues** (if parent):
- FM-101: [State] - [Last activity]
- FM-102: [State] - [Last activity]

**Next Actions**:
[Based on assessment]

**Recommended next command**: `/logging` or `/context_gathering` [with rationale]
```

## Parent Issue Resume

When resuming a parent issue:

```markdown
**Resuming Parent Issue**: FM-100 (Authentication System Epic)

**Sub-Issue Status Enumeration**:
1. FM-101 (JWT Implementation) - State: Done - Completed 2024-01-15 14:30 ✓
2. FM-102 (OAuth Integration) - State: In Progress - Last activity 2024-01-15 15:30 - **HAS BLOCKER** 🚫
3. FM-103 (Session Management) - State: Todo - No activity

**Blocker Analysis**:
- Reviewed FM-102 blocker: OAuth provider API endpoint changed
- Impact: FM-102 blocked, FM-103 depends on OAuth flow
- Mitigation: Coordinate with platform team for updated OAuth endpoint

**Coordination Plan**:
- [ ] Escalate FM-102 blocker to platform team (@john)
- [ ] If blocker resolves quickly: continue FM-102
- [ ] If blocker takes > 2 days: explore alternative OAuth provider
- [ ] FM-103 remains blocked until FM-102 unblocked (hard dependency)

**Next Action**: Escalate blocker, then wait for resolution before resuming FM-102

**Recommended next command**: `/startup {"issue":{"id":"FM-102"}}` (after blocker escalation)
```

## Context Sufficiency Checklist

Before choosing next mode:

```markdown
**Context Sufficiency Assessment**:
- [ ] Recent Context: Latest comment < 48h old ✓
- [ ] Current Summary: Context Review Summary validated ✓
- [ ] Success Criteria: Specific and measurable ✓
- [ ] Integration Points: Documented with evidence ✓
- [ ] Risks Resolved: No unresolved blockers ✓
- [ ] Confidence ≥95%: 6/6 criteria met ✓

**Decision**: Context sufficient, proceed to implementation

**Recommended next command**: `/logging` to continue work
```

## Confidence-Based Branching

**<67% confidence**:
```markdown
🛑 CLARIFICATION REQUIRED - Confidence 50% (3/6 criteria)

[Structured clarification request - see startup.md for format]

**Recommended next command**: WAIT for user response
```

**83% confidence**:
```markdown
⚠️ APPROVAL NEEDED - Confidence 83% (5/6 criteria)

Missing: Integration Points documentation

**Options**:
1. Research codebase for integration patterns (autonomous)
2. Request documentation from team (requires coordination)

**Recommended**: Option 1 - run `/context_gathering` for integration research

**Question**: Should I proceed with codebase research, or wait for team documentation?
```

**≥95% confidence**:
```markdown
**Confidence**: 100% (6/6 criteria) - Proceeding autonomously

**Recommended next command**: `/logging` to continue implementation
```

## Mode Selection Decision

**Branch to `/startup`** when:
- Issue is still in backlog/Todo (not active)
- Fresh status transition needed
- Context reset required

**Branch to `/context_gathering`** when:
- Context Review Summary missing or outdated
- Confidence <95% due to missing context
- New requirements or scope changes detected

**Branch to `/logging`** when:
- Context is current and sufficient
- Confidence ≥95%
- Ready to continue implementation

**Branch to `/code_review`** when:
- Implementation complete
- Ready for review before completion

**Branch to `/completion`** when:
- All work done
- Quality gates passed
- Ready to close issue

## Related Protocols
- `resume.md` - Detailed resume protocol
- `sub-issue-governance.md` - Parent/child enumeration rules
- `universal-agent.md` - Confidence calculation

## Examples

```bash
# Resume work on an issue
/resume {"issue":{"id":"FM-123"}}

# Resume parent issue (will enumerate children)
/resume {"issue":{"id":"FM-100"}}
```

## State Updates

After `/resume`, `.flow-maestro/cursor.json` is updated:

```json
{
  "issue_id": "FM-123",
  "mode": "resume",
  "last_comment_cursor": "2024-01-15T16:00:00Z",
  "updated_at": "2024-01-15T16:05:00Z"
}
```

