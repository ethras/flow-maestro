# Parent-Child Information Flow Protocol

This protocol guides agents on interpreting parent/child data provided by the server.

## Quick Reference
- [Parent → Child Flow](#parent--child-flow)
- [Child → Parent Notifications](#child--parent-flow)
- [Parent Completion Aggregation](#parent-completion-with-child-aggregation)
- [Parent Launch Enumeration](#parent-launch-with-child-activity)

## Core Principle
**Server provides data structure, agent provides semantic interpretation.**

> **Strategos Alignment**: Parent/child coordination must reference the Evidence Ledger defined in `protocols/strategos-prime.md`. During Phase II (Deep Reconnaissance), capture cross-issue observations; during Phase IV (Final Seal), summarise child outcomes with ledger citations.

The server fetches and structures parent/child information from Linear. The agent interprets this data, extracts relevant context, and decides what information to propagate between parent and child issues.

## Parent → Child Flow

### Data Provided by Server

When starting a child issue (sub-issue), the server includes `data.parent_snapshot` with:

- **`issue`**: Parent issue metadata (id, identifier, title, description, updatedAt)
- **`comments`**: Full parent comment history (oldest → newest)
- **`siblings`**: Other child issues for integration awareness
- **`cursors`**: Pagination cursors for parent comments

### Agent Interpretation Rules

You must interpret parent context to extract what's relevant for this child. Use these rules:

1. **Temporal Relevance**: Prioritize parent context < 7 days old
2. **Direct References**: Extract comments mentioning this child's identifier
3. **Structural Markers**: Look for "## Context Manifest", "## Decisions" headers
4. **Semantic Tags**: Extract "CROSS-CUTTING:", "ALL-CHILDREN:" tags
5. **Constraint Keywords**: Extract "must", "requirement", "constraint" from parent description/manifests

### What to Propagate to Child

**Always include in child Context Review Summary**:
- Parent architectural decisions affecting implementation approach
- Shared constraints (security, performance, API contracts)
- Integration points with siblings
- Parent acceptance criteria applicable to child scope

**Never include**:
- Entire parent comment history (summarize instead)
- Implementation detail from siblings (causes coupling)
- Irrelevant parent coordination notes

### Example: Child Context Review with Parent Reference

```markdown
## Context Review Summary

**Parent Context** (from FM-100):
- Per parent manifest (2024-01-14 10:00): All auth components must use shared AuthConfig interface
- Shared constraint: Token expiry ≤ 15 minutes per security requirements
- Integration with FM-102 (OAuth): Must provide token validation interface
- Parent acceptance criteria: All components must pass security review before completion

**This Child's Scope**: Implement JWT token generation service
- Generate RS256 tokens with configurable expiry
- Implement token validation interface for sibling integration
- Use shared AuthConfig per parent requirement

**Plan**: 
1. Define AuthConfig interface (coordinate with parent if not exists)
2. Implement JWT service using RS256
3. Create token validation interface for FM-102 integration
4. Add unit tests including security edge cases
```

---

## Child → Parent Flow

### Data Provided by Server

After posting a child work log, the server includes `meta.parent_context` with:

- **`parent_id`**: Parent issue ID
- **`parent_identifier`**: Parent issue identifier (e.g., FM-100)
- **`last_parent_activity`**: Timestamp of last parent work log
- **`parent_state`**: Current parent issue state

### Agent Decision Rules

You must decide if parent notification is warranted based on significance:

**Post parent notification when**:
1. Child work log contains blockers requiring coordination
2. Child reaches major milestone/completion
3. Child makes decisions affecting siblings
4. Child discovers integration impacts on other children
5. Child invalidates parent assumptions

**Do NOT notify parent when**:
- Routine progress (implementation work without blockers/impacts)
- Minor bug fixes not affecting other children
- Code refactoring within child scope
- Normal quality gate execution

### Parent Notification Format

When parent notification is warranted, call the `/progress` command (targeting the parent issue) with this format:

```markdown
## 🔗 Child Update: ${child.identifier}

**Event**: [BLOCKER | MILESTONE | DECISION | COMPLETION | INTEGRATION_IMPACT]
**Timestamp**: ${timestamp}

**Summary**: [One sentence description]

**Impact**: [Who/what this affects - siblings, dependencies, parent scope]

**Details**: See ${child.identifier} (${timestamp}) for full context
```

**Token Efficiency**: Parent notifications should be ≤100 tokens. Reference child log by timestamp, don't duplicate detail.

### Example: Child Notifying Parent of Blocker

```markdown
## 🚫 Child Update: FM-102

**Event**: BLOCKER
**Timestamp**: 2024-01-15 15:30

**Summary**: OAuth provider API changed, endpoint /v2/oauth/authorize not available

**Impact**: FM-102 blocked, affects integration with FM-103 (session management depends on OAuth flow)

**Details**: See FM-102 (2024-01-15 15:30) for full blocker analysis and mitigation options
```

---

## Parent Completion with Child Aggregation

### Data Provided by Server

When completing a parent issue, the server includes `data.child_completion_data` with:

- **`identifier`**: Child issue identifier
- **`title`**: Child issue title
- **`completed_at`**: Completion timestamp
- **`completion_comment`**: Reference to child's Final Completion Summary (id, timestamp)
- **`quality_gates_detected`**: Best-effort extraction of lint/test/build results

### Agent Aggregation Rules

You must aggregate child completions into parent Final Completion Summary:

**Include for each child**:
- Child identifier + completion timestamp
- Quality gate status (if available)
- Reference to child completion comment

**Aggregated verification**:
- Cross-child integration testing results
- Security review spanning all children
- Overall quality gate summary

### Example: Parent Final Completion Summary

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
```

---

## Parent Launch with Child Activity

### Data Provided by Server

When starting a parent issue, the server includes `data.child_activity` with:

- **`identifier`**: Child issue identifier
- **`title`**: Child issue title
- **`state`**: Current child state name
- **`stateType`**: Child state type (completed/started/etc.)
- **`last_activity`**: Timestamp of last work log (if any)
- **`has_blocker`**: Boolean indicating if child has active blockers

### Agent Enumeration Rules

You must enumerate all children before deciding coordination actions:

**Enumerate with assessment**:
```markdown
**Sub-Issue Status**:
- FM-101: Done (completed 2024-01-15) ✓
- FM-102: In Progress (last activity 2 hours ago, **HAS BLOCKER** 🚫)
- FM-103: Todo (no activity)
```

**Review blocked children**:
- If `has_blocker: true`, run `/launch {"issue":{"id":"<child-id>","mode":"resume"}}` to review blocker details
- Assess if blocker requires parent-level coordination
- Document coordination plan in parent work log

**Plan coordination work**:
- Which child to start next (consider dependencies)
- Cross-cutting work affecting multiple children
- Dependency sequencing between children

### Example: Parent Enumeration and Coordination Planning

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
- [ ] If blocker takes > 2 days: explore alternative OAuth provider or refactor dependency
- [ ] FM-103 remains blocked until FM-102 unblocked (hard dependency)

**Next Action**: Escalate blocker, then wait for resolution before resuming FM-102
```

---

## Information Taxonomy

### Parent-Level Information (Coordination)

Information that should live on parent issues:

- Epic/feature architecture (high-level)
- Cross-cutting decisions affecting multiple children
- Shared constraints/requirements
- Dependency tracking between children
- Child completion status aggregation
- Blockers requiring coordination/escalation
- Integration verification spanning multiple children

### Child-Level Information (Implementation)

Information that should live on child issues:

- Code changes and technical decisions
- Quality gate results
- Detailed verification steps
- Implementation discoveries/blockers
- Integration point implementations
- Bug fixes and workarounds
- Test results and coverage

---

## Decision Framework

### When Starting Work

**On Parent**: 
1. Enumerate children using `data.child_activity`
2. Assess blocked children
3. Select child to work on
4. Call `/launch` on selected child

**On Child**: 
1. Review `data.parent_snapshot`
2. Extract relevant parent context
3. Reference parent decisions in child Context Review Summary
4. Proceed with implementation

### When Logging Work

**On Parent**: 
- Log coordination only (cross-cutting work, blocker escalation, dependency management)
- Reference children by identifier+timestamp
- Do NOT log implementation detail

**On Child**: 
- Log ALL implementation detail
- Review `meta.parent_context` after posting
- Decide if parent notification warranted based on significance
- If warranted, post parent notification using prescribed format

### When Completing Work

**On Parent**: 
- Review `data.child_completion_data`
- Aggregate child completions in Final Completion Summary
- Reference all children by identifier+timestamp
- Include aggregated quality gates and cross-child verification

**On Child**: 
- Complete normally using standard completion process
- Parent aggregation happens automatically when parent completes

---

## Common Anti-Patterns

### ❌ Over-Propagation

**Problem**: Copying entire parent comment history into child Context Review Summary

**Why it's wrong**: Wastes tokens, creates maintenance burden, violates DRY principle

**Correct approach**: Extract and summarize only relevant parent decisions/constraints

---

### ❌ Under-Notification

**Problem**: Not notifying parent when child is blocked, causing parent to have outdated understanding

**Why it's wrong**: Reduces visibility, delays escalation, blocks sibling work

**Correct approach**: Post parent notification when blockers require coordination

---

### ❌ Excessive Notifications

**Problem**: Notifying parent on every routine progress update

**Why it's wrong**: Creates noise, dilutes significance of important notifications

**Correct approach**: Only notify on significant events (blockers, milestones, decisions, completion, integration impacts)

---

### ❌ Missing Sibling Context

**Problem**: Implementing child without reviewing sibling integration points from parent snapshot

**Why it's wrong**: Causes integration failures, rework, inconsistent interfaces

**Correct approach**: Review `data.parent_snapshot.siblings` and note integration points in child Context Review Summary

---

## Quick Reference

### Child Launch with Parent Context

```markdown
1. Review `data.parent_snapshot.comments` (newest → oldest)
2. Extract: manifests < 7 days, decisions, constraints, sibling integration points
3. Post Context Review Summary with parent references
4. Format: "Per parent ${id} (${timestamp}): ${summary}"
```

### Child Logging with Parent Notification Decision

```markdown
1. Post child work log normally
2. Review `meta.parent_context` in response
3. Evaluate: blocker? milestone? decision affecting siblings? integration impact?
4. If yes → post parent notification (≤100 tokens, reference child log timestamp)
5. If no → continue working
```

### Parent Completion with Child Aggregation

```markdown
1. Review `data.child_completion_data` (all terminal children)
2. For each child: identifier + timestamp + quality gates (if available)
3. Add aggregated verification (integration tests, security review)
4. Reference all children in Final Completion Summary
```

### Parent Launch with Child Enumeration

```markdown
1. Review `data.child_activity` (all children)
2. Enumerate: identifier + state + last_activity + has_blocker
3. Review blocked children (run `/launch` if coordination needed)
4. Plan: which child to work on next, dependencies, cross-cutting work
```

---

## Related Protocols

- **sub-issue-governance** protocol: Complete parent/child workflow rules and discipline
- **task-launch** protocol: Launch protocol with parent/child context sections
- **/progress** protocol: Logging protocol with parent notification guidance
- **task-completion** protocol: Completion protocol with child aggregation guidance
- **universal-agent** protocol: Core agent principles including information flow
