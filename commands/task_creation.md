---
description: Create new Linear issues with proper structure and governance
argument-hint: {"issue":{"id":"<parent-id>"},"task_details":{...}}
---

# `/task_creation` — Create Linear Issues

## Linear MCP Workflow

1. **Draft Task**: Use universal task template (see `protocols/universal-task-template.md`)
   - **Summary**: One-sentence WHAT and WHY
   - **Success Criteria**: Measurable acceptance criteria
   - **Impacted Modules**: List affected components
   - **Verification Plan**: How to verify completion

2. **Create Issue**: `create_issue_linear(team: "<team-key>", project: "<project-key>", title: "...", description: "...", ...)`
   - Set title, description (with template)
   - Set priority, labels, team, project using the string identifiers returned by `list_teams_linear` / `list_projects_linear`
   - Set `parentId` if creating child issue (use the issue ID string, e.g., `"FM-123"`)

> ℹ️ **Linear Parameter Reference**
> - `team`: Team key or name from `list_teams_linear`
> - `project`: Project name from `list_projects_linear`
> - `parentId`: Issue identifier string for parent/child links

3. **Verify Creation**: Confirm issue created with correct structure

4. **Update State**: Write cursor to `.flow-maestro/cursor.json`

---

## Universal Task Template

All tasks must follow this structure:

```markdown
## Summary
[One-sentence WHAT and WHY]

## Success Criteria
- [ ] Criterion 1 (measurable)
- [ ] Criterion 2 (measurable)
- [ ] Criterion 3 (measurable)

## Impacted Modules
- Module 1: [path/to/module]
- Module 2: [path/to/module]

## Verification Plan
- Unit tests: [description]
- Integration tests: [description]
- Manual QA: [steps]
```

---

## Expected Output

```markdown
## Task Created: FM-124 - Implement Token Refresh Endpoint

**Issue Details**:
- Identifier: FM-124
- Title: Implement Token Refresh Endpoint
- Priority: High
- Parent: FM-123 (JWT Token Service)
- Team: Engineering
- Project: Authentication System

**Description**: Follows universal template
- Summary: ✓
- Success Criteria: ✓ (3 criteria)
- Impacted Modules: ✓
- Verification Plan: ✓

**Created in Linear**: https://linear.app/team/issue/FM-124

**Next**: `/startup {"issue":{"id":"FM-124"}}` (start work) or `/task_creation` (create more)
```

---

## Parent/Child Task Creation

### Creating Parent (Epic/Meta Issue)

1. Draft parent using universal template (high-level)
2. Call `create_issue_linear` without `parentId`
3. Create children with `parentId` set to parent ID

```markdown
**Parent Created**: FM-100 - Authentication System Epic

**Children to Create**:
1. FM-101: JWT Implementation
2. FM-102: OAuth Integration
3. FM-103: Session Management

**Next**: `/task_creation` (create children)
```

### Creating Children

```bash
# Create child 1
/task_creation {"task_details":{"title":"Implement JWT Service","description":"[Template]","priority":"High","parentId":"FM-100","team":"Engineering","project":"Authentication System"}}

# Create child 2
/task_creation {"task_details":{"title":"Implement OAuth Integration","description":"[Template]","priority":"High","parentId":"FM-100","team":"Engineering","project":"Authentication System"}}
```

---

## Task Creation from PRP (Product Requirements Proposal)

When creating tasks from PRP:

1. **Read PRP**: Extract requirements, scope, acceptance criteria
2. **Determine Structure**: Single task or parent + children?
3. **Draft Tasks**: Use universal template for each
4. **Create in Linear**: Call `create_issue_linear` for each
5. **Link PRP**: Include PRP URL in description

```markdown
**PRP**: https://github.com/org/repo/pull/123

**Tasks Created**:
- FM-100 (Parent): Authentication System Epic
- FM-101 (Child): JWT Implementation
- FM-102 (Child): OAuth Integration
- FM-103 (Child): Session Management

**Next**: `/startup {"issue":{"id":"FM-101"}}` (start first child)
```

---

## Confidence Assessment for New Tasks

Before creating, ensure:

```markdown
**Confidence Assessment**: 100% (6/6 criteria)
1. ✅ Success Criteria: Defined in template
2. ✅ Integration Points: Identified in Impacted Modules
3. ✅ Pattern Consistency: Referenced in description
4. ✅ Risk Mitigation: Documented in description
5. ✅ Sub-Issue Alignment: Parent/child structure clear
6. ✅ Verification Plan: Documented in template

**Ready to Create**: Yes
```

---

## Next Command Logic

- **Task created, ready to start**: `/startup {"issue":{"id":"<new-id>"}}`
- **More tasks to create**: `/task_creation` (create next)
- **Parent created, create children**: `/task_creation` (with `parentId`)
- **All tasks created**: `/startup` on first task

---

## Reference

- **Protocols**: `protocols/universal-task-template.md`, `protocols/sub-issue-governance.md`
- **Linear MCP**: `create_issue_linear`, `list_teams_linear`, `list_projects_linear`
- **Template**: See `protocols/universal-task-template.md`
