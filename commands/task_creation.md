---
description: Create new Linear issues with proper structure and governance
argument-hint: {"task_details":{"title":"<title>","description":"<template>","priority":"High","team":"<team-key>","project":"<project-name>","parentId":"<optional-parent>"}}
---

# `/task_creation` — Create Linear Issues

## Pre-Draft Planning Checklist

Run a structured planning pass before writing anything into the universal template. Capture these checkpoints in your scratchpad or Linear draft so downstream agents inherit the thinking:

1. **Observations** – Cite verified facts (repo paths, existing patterns, stakeholder notes). Example: `apps/web/nx-zero.config.ts` already defines deployment targets.
2. **Key Findings** – Enumerate risks, unknowns, dependencies blocking scope clarity. If anything critical remains unresolved, pause and gather data before proceeding.
3. **Approach** – Describe the implementation strategy in 2-3 bullet points, calling out defensive considerations and alignment with shared protocols.
4. **Proposed File Changes** – List targeted files/modules with planned modifications. Include justifications that tie back to observed patterns.
5. **Verification Notes** – Document tests, build steps, and manual QA you will require. Flag open TODOs that need follow-up ownership.

Only continue to the Linear MCP workflow after you are ≥95% confident each section above is complete and consistent.

## Linear MCP Workflow

1. **Draft Task**: Use universal task template (see `protocols/universal-task-template.md`)
   - Paste the planning checklist output into the matching sections (`Observations`, `Key Findings`, `Approach`, `Proposed File Changes`, `Verification Notes`).
   - Translate planning notes → Template summary blocks:
     - **Summary**: Condense the Approach’s primary objective and rationale.
     - **Success Criteria**: Promote Key Findings into measurable acceptance checks (include mitigation items where applicable).
     - **Impacted Modules**: Pull from Proposed File Changes (paths, services, shared libs).
     - **Verification Plan**: Copy Verification Notes, refined into lint/test/QA tasks.

   Example:

   ```markdown
   ## Observations
   - `apps/web/nx-zero.config.ts` already defines deployment targets
   - Prior HR features wrap create/edit buttons with `HasPermission`

   ## Key Findings
   - No permission checks on entities/items CRUD → add guards before exposing buttons
   - Deployment flow depends on auth store permissions array

   ## Approach
   - Layered defense: UI gating, handler guards, mutation checks
   - Mirror HR feature patterns for consistency

   ## Proposed File Changes
   - `features/entities/pages/ListPage.tsx`: wrap create button with permission check
   - `features/entities/components/forms/EntityFormModal.tsx`: guard onCreate/onUpdate

   ## Verification Notes
   - Automated: `pnpm test --filter permissions` (or equivalent)
   - Manual: attempt CRUD with/without permissions in staging seed account
   - TODO: Confirm copy translations with Product before release
   ```

2. **Create Issue**: `create_issue_linear(team: "<team-key>", project: "<project-key>", title: "...", description: "...", ...)`
   - Required keys for `task_details`: `title`, `description`, `priority`, `team`, `project`
   - Optional keys: `parentId`, `labels`, `dueDate`, `estimate`
   - Retrieve `team` and `project` identifiers via `list_teams_linear` and `list_projects_linear`
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
