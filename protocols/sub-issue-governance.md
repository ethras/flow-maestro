# Sub-Issue Governance Protocol

This protocol defines how Flow Maestro agents handle parent/child issue hierarchies in Linear, ensuring clear ownership, traceability, and quality across multi-issue workflows.

## Quick Reference
- [Launch Discipline](#1-launch-discipline-mandatory)
- [Progress Discipline](#2-progress-discipline-mandatory)
- [Sealing Sequencing](#4-sealing-sequencing-mandatory)
- [Blocked State Handling](#6-blocked-state-handling-mandatory)

## Core Principle

**Sub-issues are the atomic unit of work. Parent issues are coordination umbrellas.**

Every unit of implementation, testing, documentation, and verification happens at the sub-issue level. Parent issues exist solely to organize, track, and reference the work done in their children.

> **Strategos Alignment**: During Phase III (Masterplan Forging), outline sub-issue sequencing with explicit Evidence Ledger references. During Phase IV (Final Seal), audit parent readiness using the confidence checklist in `protocols/shared-templates.md`.

## Glossary

- **Parent Issue / Epic**: A Linear issue that has one or more sub-issues attached. Contains no direct implementation work.
- **Sub-Issue / Child**: A Linear issue that is a child of a parent. Contains all implementation detail.
- **Terminal State**: A Linear issue state with type `completed` or `canceled`.
- **Non-Terminal State**: Any state that is not terminal (e.g., `unstarted`, `started`, `backlog`).
- **Atomic Unit of Work**: A single sub-issue representing 1-4 hours of focused implementation.

## Parent/Child Relationship Rules

### 1. Launch Discipline (MANDATORY)

**Rule**: Before editing code, running migrations, or producing documentation tied to a sub-issue, you MUST run `/launch` for that specific sub-issue.

**Process**:
1. If you receive a parent issue, enumerate all `data.linear.issue.subIssues`.
2. Review each sub-issue's current state, scope, and last activity.
3. Select the sub-issue you intend to work on.
4. Call `launch({ issue: { id: "<sub-issue-id>", mode: "start" } })` for that child.
5. Proceed with implementation only after the launch completes with ≥95% confidence.

**Violations**:
- ❌ Starting work on a parent issue without launching a child
- ❌ Implementing features without individual sub-issue context
- ❌ Assuming parent launch is sufficient for child work

**Valid Patterns**:
- ✅ Parent launch → enumerate children → select child → child launch → implement
- ✅ Direct child launch when you already know the sub-issue identifier

### 2. Progress Discipline (MANDATORY)

**Rule**: Post `/progress` logs on the specific sub-issue(s) affected. Parent logs should only summarize cross-cutting work and reference child logs by timestamp.

**Sub-Issue Progress Logging** (where implementation happens):
- ✅ All code changes
- ✅ All decisions and rationale
- ✅ All quality gate results (lint/test/build)
- ✅ All discoveries and blockers
- ✅ All verification steps
- ✅ Complete "Work Log Update" with all sections populated

**Parent Progress Logging** (coordination only):
- ✅ Cross-cutting work affecting multiple children
- ✅ References to child logs: "See FM-123 (2024-01-15 14:00) for API implementation"
- ✅ Epic-level decisions impacting all children
- ✅ Dependency tracking between children
- ❌ Implementation detail (should be in children)
- ❌ Code change lists (should be in children)
- ❌ Quality gate results (should be in children)

**Progress Reference Format**:
```markdown
## Work Log Update - 2024-01-15 16:00 - (Agent)

#### Completed
- Coordinated authentication flow across sub-issues
- See FM-456 (2024-01-15 14:30) for JWT implementation
- See FM-457 (2024-01-15 15:15) for OAuth integration

#### Next Steps
- Resume FM-458 for session management
```

**Violations**:
- ❌ Logging implementation detail on parent
- ❌ Duplicating sub-issue logs on parent
- ❌ Logging on parent when only one child was touched

### 3. Context Manifest Placement (MANDATORY)

**Rule**: Technical context and implementation details live with the sub-issue. Parents contain only cross-cutting manifests or indexes pointing to child summaries.

**Sub-Issue Context Manifests** (technical detail):
- ✅ Code architecture and entry points
- ✅ Integration points and API contracts
- ✅ Dependencies and external libraries
- ✅ Implementation patterns and conventions
- ✅ Testing strategy and verification steps
- ✅ Security considerations and performance notes

**Parent Context Manifests** (coordination):
- ✅ Overall feature architecture (high-level)
- ✅ Index of sub-issue manifests with links
- ✅ Cross-cutting concerns affecting all children
- ✅ Epic-level acceptance criteria
- ❌ Detailed technical implementation (should be in children)

**Example Parent Manifest**:
```markdown
## Context Manifest - Parent Issue

### Feature: Authentication System

**Architecture Overview**:
Multi-component authentication system split across 3 sub-issues.

**Sub-Issue Context Manifests**:
- FM-456: JWT Implementation (see manifest dated 2024-01-15 14:00)
- FM-457: OAuth Integration (see manifest dated 2024-01-15 15:00)
- FM-458: Session Management (pending launch)

**Cross-Cutting Concerns**:
- All components must use shared `AuthConfig` interface
- Security review required before sealing
- Integration tests span all three components
```

### 4. Sealing Sequencing (MANDATORY)

**Rule**: Sub-issues must reach terminal state via `/seal`. Parents can only move to Review/Done after ALL children are sealed.

**Sub-Issue Sealing Process**:
1. Complete implementation work on the sub-issue.
2. Run quality gates (lint/test/build) and record results.
3. Post a final `/progress` log summarizing outcomes.
4. Execute `/review` and resolve all 🔴 findings.
5. Call `/seal {"issue":{"id":"<child-id>"}}` and ensure the Evidence Ledger is clear.
6. Record the seal timestamp in sub-issue comments.

**Parent Sealing Process**:
1. Verify EVERY sub-issue in `data.linear.issue.subIssues` is in a terminal state.
2. Confirm no children remain "In Progress" or "Blocked".
3. Post a parent "Final Completion Summary" referencing each child seal:
   ```markdown
   ## Final Completion Summary
   
   **Sub-Issue Status**:
   - FM-456: Sealed 2024-01-15 14:30 (all gates pass)
   - FM-457: Sealed 2024-01-15 15:45 (lint override documented)
   - FM-458: Sealed 2024-01-15 17:00 (all gates pass)
   
   **Verification**:
   - All child quality gates satisfied
   - Integration tests across components: PASS
   - Security review: PASS (see `/review` comment 2024-01-15 17:30)
   ```
4. Execute `/seal {"issue":{"id":"<parent-id>"}}`, citing child summaries and Evidence Ledger closure.

**Violations**:
- ❌ Attempting parent seal while children are non-terminal
- ❌ Sealing parent without referencing child seal timestamps
- ❌ Skipping individual sub-issue quality gates

**Enforcement**:
Parents must block sealing if any child lacks a `/seal` record or remains non-terminal.

### 5. Quality Gate Attribution (MANDATORY)

**Rule**: Report lint/test/build results on the sub-issue you worked on. Parent seals must reference child gate results.

**Sub-Issue Quality Gates**:
```markdown
## Work Log Update - 2024-01-15 14:00 - (Agent)

#### Completed
- Implemented JWT service
- Added unit tests for token generation

#### Quality Gates
- Lint: PASS
- Test: PASS (12 new tests, all passing)
- Build: PASS
```

**Parent Quality Gate Summary**:
```markdown
## Final Completion Summary

**Quality Gates (Aggregated)**:
- FM-456: All gates pass (see log 2024-01-15 14:30)
- FM-457: Lint overridden due to legacy code (see seal comment)
- FM-458: All gates pass (see log 2024-01-15 17:00)
- Integration tests: PASS
```

### 6. Blocked State Handling (MANDATORY)

**Rule**: If a sub-issue cannot be completed, set that sub-issue's status to blocked, log the reason, and keep the parent open. Escalate blockers via parent log with links.

**Sub-Issue Blocking Process**:
1. Document the specific blocker in a Work Log Update on the sub-issue
2. Update the sub-issue status to "Blocked" (or appropriate blocked state)
3. Identify who/what can unblock (team, decision, dependency)
4. Post a coordination log on the parent referencing the blocked child

**Parent Coordination Log**:
```markdown
## Work Log Update - 2024-01-15 16:00 - (Agent)

#### Blockers
- FM-457 blocked on upstream API changes (see FM-457 log 2024-01-15 15:30)
- Waiting for Platform team to deploy endpoint /v2/oauth/authorize
- Impact: Authentication epic cannot complete until unblocked

#### Next Steps
- Coordinate with Platform team (@john) for deployment timeline
- Resume FM-458 (session management) in parallel if possible
```

**Violations**:
- ❌ Marking parent as "Done" while children are blocked
- ❌ Failing to document blocker on the specific sub-issue
- ❌ Not escalating blocker visibility to parent level

## Workflow Integration

### When Starting Work
1. If assigned a parent issue, enumerate `subIssues` immediately
2. Treat enumeration as Step 0 before planning any work
3. Run `/launch` on the specific child you'll work on
4. Never proceed with implementation without child launch

### When Logging Progress
1. Determine: am I working on a parent or child?
2. If child: log ALL implementation detail here
3. If parent: log ONLY coordination and references to children

### When Resuming Work
1. If resuming a parent, re-enumerate all `subIssues`
2. Check for state changes since last session
3. Select next child to work on
4. Call `/launch` on that child before proceeding

### When Sealing Work
1. Complete each child individually (quality gates + review)
2. Only after ALL children are sealed, prepare the parent seal
3. Parent seal must reference all child seal timestamps

## Common Anti-Patterns

### ❌ "Parent-First Progress Logs"
Recording `/progress` updates on the parent instead of the child.

**Why it's wrong**: Future agents can't trace which code belongs to which sub-issue. Context is lost.

**Correct approach**: Run `/progress` on the child, reference from the parent.

### ❌ "Assumed Parent Launch"
Starting implementation work without running `/launch` on the specific sub-issue.

**Why it's wrong**: Missing sub-issue-specific context, acceptance criteria, and history.

**Correct approach**: Always run `/launch {"issue":{"id":"<child-id>","mode":"start"}}` before implementation.

### ❌ "Premature Parent Seal"
Attempting to seal a parent while children remain non-terminal.

**Why it's wrong**: Breaks project tracking, hides incomplete work.

**Correct approach**: Seal all children first, then seal the parent referencing them.

### ❌ "Context Duplication"
Copying technical context from child to parent or vice versa.

**Why it's wrong**: Creates maintenance burden, leads to drift between copies.

**Correct approach**: Single source of truth (child), parent indexes it.

## Tool Behavior Summary

| Tool | Parent Issue Behavior | Child Issue Behavior |
|------|----------------------|---------------------|
| **launch** | Warns about sub-issues, provides governance protocol | Normal launch flow (start/resume) |
| **progress** | Context-aware guidance: "log coordination only" | Context-aware guidance: "log all detail" |
| **review** | Audits cross-cutting risk alignment | Reviews child implementation |
| **seal** | BLOCKS if children non-terminal | Normal closure flow |

## Success Criteria

A well-governed parent/child workflow exhibits:
- ✅ Each sub-issue has individual launch before implementation
- ✅ All implementation detail lives in sub-issue comments
- ✅ Parent logs reference children by identifier + timestamp
- ✅ Parent sealing blocked until all children terminal
- ✅ Quality gates reported on children, aggregated on parent
- ✅ Context manifests detailed on children, indexed on parent
- ✅ Blockers documented on affected child and escalated to parent

## Quick Reference Card

**Before working on a sub-issue**:
```
launch({ issue: { id: "<child-id>", mode: "start" } })
```

**Progress logging on a child**:
- Include: code, decisions, gates, verification
- Format: Full "Work Log Update" template

**Progress logging on a parent**:
- Include: cross-cutting work, child references
- Format: "See FM-123 (timestamp) for X"

**Sealing a child**:
- Quality gates → `/review` → Final `/progress` log → `/seal`

**Sealing a parent**:
- Verify all children sealed → Reference child seals → `/seal`

**If blocked**:
- Log on child → Update child status → Escalate on parent

## 7. Automatic Data Provisioning (NEW)

The server now provides enhanced parent/child data in tool responses to support bidirectional information flow:

### Server-Provided Data

**Child Launch** (`data.parent_snapshot`):
- Parent issue metadata, description, updatedAt
- Full parent comment history for context extraction
- Sibling issues for integration awareness
- Parent comment cursors

**Parent Launch** (`data.child_activity`):
- Child identifier, title, state, stateType
- Last activity timestamp (from last work log)
- Blocker detection flag (`has_blocker`)

**Child Progress** (`meta.parent_context`):
- Parent issue ID and identifier
- Last parent activity timestamp
- Parent state
- Enables parent notification decision

- Child identifier, title, seal timestamp
- Seal comment reference (id, timestamp)
- Quality gates detected (best-effort extraction)

### Agent Responsibility

The server provides structured data; **you interpret and decide**:

- **Parent → Child**: Extract relevant parent context for child work (see `parent-child-information-flow` protocol)
- **Child → Parent**: Decide when parent notification warranted based on significance
- **Parent Aggregation**: Aggregate child seals into parent summary

### Key Principle

**Server = Data Provider | Agent = Semantic Interpreter**

The server doesn't decide what's "relevant" or "important" - you do. Use the provided data structures to make intelligent decisions about information propagation between parent and child issues.

## Related Protocols

- **task-launch** protocol: Sub-issue detection and enumeration steps
- **progress** protocol: Parent vs child logging decision point
- **seal** protocol: Parent sealing validation rules
- **launch** protocol: Sub-issue enumeration on resume
- **universal-agent** protocol: Sub-issue governance principle in core maxims
- **parent-child-information-flow** protocol: Complete guidance on parent/child information flow
