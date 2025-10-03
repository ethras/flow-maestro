---
description: Resume work on an existing Linear issue
argument-hint: {"issue":{"id":"<issue-id>"}}
---

# `/resume` — Resume Work on Issue

## Linear MCP Workflow

1. **Fetch Latest**: `get_issue_linear(id: "<issue-id>")`
   - Check current state, priority, assignee

2. **Read New Comments**: `list_comments_linear(issueId: "<issue-id>")`
   - Delta read since last cursor (from `.flow-maestro/cursor.json`)
   - Look for new decisions, risks, status changes

3. **Assess Context**: Validate existing Context Review Summary
   - Is it current? (<7 days, no scope changes)
   - Are there new requirements or blockers?

4. **Calculate Confidence**: Re-evaluate 6 criteria with new information

5. **Update State**: Write cursor to `.flow-maestro/cursor.json`

**Note**: `/resume` NEVER changes issue state (unlike `/startup`)

---

## Expected Output

```markdown
## Resume: FM-123 - [Issue Title]

**Current Status**:
- State: In Progress
- Last Activity: 2024-01-15 16:00

**Recent Activity** (since last session):
- New comment (2024-01-15 16:00): Security review feedback
- Blocker resolved: OAuth endpoint updated

**Context Assessment**:
- Context Review Summary: Current (2024-01-15 14:00)
- Confidence: 100% (6/6 criteria)
- Blockers: None

**Next**: `/logging` (continue implementation)
```

---

## Parent Issue Resume

When resuming parent:

1. **Enumerate Children**: `list_issues_linear(parentId: "<issue-id>")`
2. **Check Child Status**: Identify blockers, completion, activity
3. **Coordinate**: Don't implement

```markdown
**Resuming Parent**: FM-100

**Sub-Issue Status**:
1. FM-101: Done ✓ (2024-01-15 14:30)
2. FM-102: In Progress - **BLOCKER** 🚫 (OAuth endpoint issue)
3. FM-103: Todo

**Action**: Address FM-102 blocker before proceeding

**Next**: `/startup {"issue":{"id":"FM-102"}}` (resolve blocker)
```

---

## Next Command Logic

- **Context current, confidence ≥95%**: `/logging` (continue work)
- **Context outdated or confidence <95%**: Gather context, update manifests
- **Blockers found**: Resolve blockers first
- **Implementation complete**: `/code_review`
- **All done**: `/completion`

---

## Reference

- **Protocols**: `protocols/sub-issue-governance.md`
- **Linear MCP**: `get_issue_linear`, `list_comments_linear`
- **State**: `.flow-maestro/cursor.json`
