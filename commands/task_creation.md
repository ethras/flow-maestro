# `/task_creation` Command

## Purpose
Create new Linear issues with proper structure, context, and alignment with parent/child governance.

## Signature
```
/task_creation {"issue":{"id":"<parent-issue-id>"},"task_details":{"title":"...","description":"...","priority":"...","parent_id":"..."}}
```

**Parameters**:
- `issue.id` (optional): Context issue for task creation
- `task_details` (required): New task details
  - `title` (required): Task title
  - `description` (required): Task description (use universal template)
  - `priority` (optional): High/Medium/Low
  - `parent_id` (optional): Parent issue ID for sub-issues
  - `team_id` (optional): Team ID
  - `project_id` (optional): Project ID
  - `labels` (optional): Array of label names
  - `assignee_id` (optional): Assignee ID

## What This Command Does

1. **Validates Task Details**
   - Ensures title is clear and specific
   - Validates description follows universal template
   - Checks for duplicate titles (if parent specified)

2. **Creates Issue in Linear**
   - Posts issue with provided details
   - Links to parent if specified
   - Applies labels and metadata

3. **Returns Created Issue**
   - Provides issue ID and identifier
   - Confirms creation success

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

**Description** (follows universal template):
- Summary: One-sentence WHAT and WHY
- Success Criteria: Measurable acceptance criteria
- Impacted Modules: Listed
- Verification Plan: Documented

**Created in Linear**: https://linear.app/team/issue/FM-124

**Recommended next command**: `/startup {"issue":{"id":"FM-124"}}` (start work) or `/task_creation` (create more tasks)
```

## Universal Task Template

All tasks must follow this structure:

```markdown
## Summary
One sentence WHAT and WHY.

## Success Criteria
- [ ] Criterion 1 (measurable)
- [ ] Criterion 2 (measurable)

## Impacted Modules/Services
- Project(s): [apps/packages]
- Modules: [list]

## Data Contracts / APIs (if applicable)
- Endpoints: [list]
- Request/Response shapes: [concise schema]

## Risks & Mitigations
- Risk: [item] → Mitigation: [plan]

## Verification Plan
- Lint/Test/Build targets
- Manual QA steps (if UI/API)

## Dependencies / Related Issues
- [links]

## Agent Compatibility & Constraints
- Capabilities required: [technology stack]
- Notes: [safety mode, test data, env]

## Context Manifest (to be populated during startup)
- Link to "Context Review Summary" comment
```

## Creating Tasks from a PRP

**Process**:
1. Draft parent/meta issue (umbrella) using universal template
2. Create parent via `/task_creation`
3. For each child task, call `/task_creation` with `parent_id` set to parent issue ID
4. Set priority/labels through task details
5. Link PRP URL or repo path in description

**Example**:

```bash
# Create parent issue
/task_creation {"task_details":{"title":"Authentication System Epic","description":"[Universal template filled]","priority":"High","team_id":"team-123","project_id":"proj-456"}}

# Create child issues
/task_creation {"task_details":{"title":"Implement JWT Service","description":"[Universal template filled]","priority":"High","parent_id":"FM-100","team_id":"team-123"}}

/task_creation {"task_details":{"title":"Implement OAuth Integration","description":"[Universal template filled]","priority":"High","parent_id":"FM-100","team_id":"team-123"}}

/task_creation {"task_details":{"title":"Implement Session Management","description":"[Universal template filled]","priority":"Medium","parent_id":"FM-100","team_id":"team-123"}}
```

## Definition of Ready (DoR)

Before moving new issue to "Todo", ensure description contains:

- **Summary**: One sentence WHAT and WHY
- **Success Criteria**: Measurable, verifiable checklist
- **Impacted Modules/Services**: Explicit list
- **Data Contracts/APIs**: Endpoints, request/response shapes (if applicable)
- **Risks & Mitigations**: Known risks with mitigation plan
- **Verification Plan**: How reviewers will verify completion
- **Dependencies/Related Issues**: Links in Linear
- **Agent Compatibility**: Labels/notes for required capabilities

## Duplicate Detection

The system blocks creation when:
- Parent already has child with same normalized title
- Recent sibling exists (7-day window)

**If Blocked**:
```markdown
❌ DUPLICATE DETECTED

**Reason**: Parent FM-100 already has child with title "Implement JWT Service"

**Existing Issue**: FM-101 (created 2024-01-10)

**Options**:
1. Adjust title to include scope qualifiers (e.g., "JWT Service - Add Token Rotation")
2. Reuse existing issue FM-101 instead of creating new one

**Recommended**: Review FM-101 to determine if it covers your scope

**Recommended next command**: `/resume {"issue":{"id":"FM-101"}}` (review existing) or retry with adjusted title
```

**Retry with Adjusted Title**:
```bash
/task_creation {"task_details":{"title":"JWT Service - Add Token Rotation","description":"[Universal template]","priority":"High","parent_id":"FM-100"}}
```

## Task Sizing Guidelines

**Create sub-issues when**:
- Estimated effort exceeds 4 hours or spans multiple components
- Work streams can progress in parallel (e.g., frontend vs. backend)
- Different skill sets or owners required for distinct deliverables

**Keep work within single issue when**:
- Changes are tightly coupled and must ship together
- Splitting would introduce more coordination overhead than value
- Effort remains within focused 1–4 hour chunk

## Priority Mapping

- **High**: Critical path, blockers, security issues
- **Medium**: Important features, improvements
- **Low**: Nice-to-haves, technical debt, documentation

## Related Protocols
- `task-creation.md` - Detailed task creation protocol
- `universal-task-template.md` - Universal task template
- `sub-issue-governance.md` - Parent/child relationship rules

## Examples

```bash
# Create standalone task
/task_creation {"task_details":{"title":"Fix authentication bug","description":"## Summary\nFix JWT token expiry validation bug\n\n## Success Criteria\n- [ ] Token expiry properly validated\n- [ ] Tests added for edge cases\n\n...","priority":"High","team_id":"team-123"}}

# Create child task under parent
/task_creation {"task_details":{"title":"Implement token refresh endpoint","description":"[Universal template filled]","priority":"High","parent_id":"FM-123","team_id":"team-123"}}

# Create task with labels
/task_creation {"task_details":{"title":"Add OAuth provider","description":"[Universal template filled]","priority":"Medium","labels":["authentication","oauth","backend"],"team_id":"team-123"}}
```

## State Updates

After `/task_creation`, `.flow-maestro/cursor.json` is NOT updated (task creation doesn't change current workflow state).

To start work on newly created task:

```bash
/startup {"issue":{"id":"FM-124"}}
```

