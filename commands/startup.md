---
description: Start work on a Linear issue and establish context
argument-hint: {"issue":{"id":"<issue-id>"}}
---

# `/startup` — Start Work on Linear Issue

## Linear MCP Workflow

1. **Fetch Issue**: `get_issue_linear(id: "<issue-id>")`
   - Extract title, description, labels, priority, parent/child links

2. **Read Comments**: `list_comments_linear(issueId: "<issue-id>")`
   - Audit oldest → newest for Context Manifests, decisions, risks
   - Summarize 2-3 key findings

3. **Update Status** *(if applicable)*: `update_issue_linear(id: "<issue-id>", state: "In Progress")`
   - Skip when the issue is a parent/coordination umbrella
   - Skip when the issue already sits in Review/Done or another assignee owns the state

4. **Calculate Confidence** (6 criteria):
   - ✅/❌ Success Criteria Clarity (cite evidence)
   - ✅/❌ Integration Points Documented
   - ✅/❌ Pattern Consistency
   - ✅/❌ Risk Mitigation
   - ✅/❌ Sub-Issue Alignment
   - ✅/❌ Verification Plan
   
   **Threshold**: ≥95% (6/6 or 5/6) to proceed

5. **Update State**: Write `.flow-maestro/cursor.json`
   - If the filesystem is read-only, note "cursor pending (read-only env)" in your response instead

---

## Parent vs Child Handling

### Child Issue Startup
- Review parent context from `get_issue_linear` parent field
- Extract parent requirements, constraints, sibling integration points
- Reference parent in Context Review Summary

### Parent Issue Startup
- Enumerate all children via `list_issues_linear(parentId: "<issue-id>")`
- Check child states, blockers, completion status
- Coordinate, don't implement

---

## Expected Output

```markdown
## Startup: FM-123 - [Issue Title]

**Issue Details**:
- Priority: [High/Medium/Low]
- State: In Progress (updated)
- Parent: [FM-100] or None
- Children: [FM-124, FM-125] or None

**Comment Audit** (2-3 bullets):
- Context Manifest found (2024-01-15 14:00): Auth patterns documented
- Prior decision: Use JWT RS256 per security review
- No unresolved blockers

**Confidence Assessment**: 100% (6/6 criteria)
1. ✅ Success Criteria: 3 acceptance criteria in description
2. ✅ Integration Points: Auth middleware, UserService identified
3. ✅ Pattern Consistency: JWT pattern in src/services/TokenService.ts:15-40
4. ✅ Risk Mitigation: Token rotation tracked in FM-125
5. ✅ Sub-Issue Alignment: No sub-issues
6. ✅ Verification Plan: Unit + integration tests documented

**Next**: `/logging` (begin implementation)
```

---

## Confidence <95% — STOP

If confidence <95%, STOP and gather context using the shared checklist in `protocols/shared-templates.md`:

1. Identify which criteria failed (cite evidence)
2. List concrete research targets or stakeholders to unblock them
3. Decide whether to pause, escalate, or schedule follow-up work
4. Post a coordination log if the blocker affects parent/child issues
5. Retry `/startup` only after missing facts are collected

```markdown
**Confidence Assessment**: 67% (4/6 criteria)
1. ✅ Success Criteria: Defined
2. ❌ Integration Points: Auth middleware not documented — need owner confirmation
3. ✅ Pattern Consistency: Found
4. ❌ Risk Mitigation: No risk analysis — requires security review link
5. ✅ Sub-Issue Alignment: N/A
6. ✅ Verification Plan: Defined

**Action**: STOP — Reach out to @owner for middleware docs; review security risk log

**Next**: `/logging` (capture blocker) or `/resume` once data gathered
```

---

## Next Command Logic

- **Confidence ≥95%**: `/logging` (begin work)
- **Confidence <95%**: Gather context, then retry `/startup`
- **Blockers found**: Resolve blockers, update Linear, then `/resume`

---

## Reference

- **Protocols**: `protocols/sub-issue-governance.md`, `protocols/parent-child-information-flow.md`
- **Linear MCP**: `get_issue_linear`, `list_comments_linear`, `update_issue_linear`, `list_issues_linear`
- **Confidence**: See `/onboarding` Step 3
