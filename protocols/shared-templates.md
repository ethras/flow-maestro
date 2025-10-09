# Shared Templates — File-Based Flow Maestro

Use these skeletons when updating change folders. Each template aligns with the `/ideate → /plan → /work → /qa` loop and assumes state lives in `.flow-maestro/projects/<project>/changes/<change-id>/`.

---

## `spec.md`

```markdown
# Change: <change-id>

## Problem
- …

## Desired Outcome
- …

## Constraints
- …

## Success Signals
- …

## Open Questions
- [NEEDS CLARIFICATION: …]
```

---

## `plan.md`

```markdown
# Implementation Plan

## Goals
- …

## Approach
- …

## Dependencies
- …

## Risks
- Risk → Mitigation

## Verification
- Automated checks
- Manual spot checks
```

---

## `tasks.md`

```markdown
## 1. Implementation
- [ ] 1.1 …
- [ ] 1.2 …

## 2. Follow-up
- [ ] 2.1 …
```

Mark blockers with `[BLOCKED]` and include owners when possible.

---

## Delta Specs (`specs/<capability>/spec.md`)

```markdown
## ADDED Requirements
### Requirement: Name
Full requirement text.

#### Scenario: Primary success
- **WHEN** …
- **THEN** …

## MODIFIED Requirements
### Requirement: Existing name
Updated requirement text.

#### Scenario: Updated behavior
- …

## REMOVED Requirements
### Requirement: Old behavior
**Reason**: …
```

Include at least one scenario per requirement and keep modifications limited to the behavior that changes.

---

## `qa.md`

```markdown
# QA Review — <date>

## Scope
- …

## Automated Verification
- Command → Result

## Manual Verification
- Scenario → Outcome

## Findings
- 🔴 Critical: …
- 🟡 Warning: …
- 🟢 Note: …

## Verdict
✅ READY / ❌ BLOCKED — rationale

**Next**: flowm specs apply <change-id>
```

---

## Timeline Entries (`timeline.jsonl`)

Append JSON per event:

```json
{"timestamp": "2025-10-09T18:00:00Z", "command": "plan", "summary": "Plan locked; 6 tasks queued"}
```

These entries feed dashboards and give reviewers a quick change history.
