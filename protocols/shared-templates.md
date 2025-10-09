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

## Summary
- Problem: …
- Desired outcome: …
- Confidence: …

## Research & Discovery
- Code search: `rg …`
- Existing flow: `path:line`
- Context7 (optional): library/topic/tokens

## Change Outline
- File/module → pseudo-steps or snippet
- …

## Tests & Validation
- Automated commands
- Manual scenarios

## Risks & Mitigations
- Risk → Mitigation/owner

## Follow-ups
- Docs, rollout, comms
```

---

## `tasks.md`

```markdown
## 0. Discovery
- [ ] 0.1 Audit current behaviour
  - Files: `…`
  - Findings: …
- [ ] 0.2 Context capture
  - Docs/specs: …
  - Context7 request (optional): library/topic/tokens

## 1. Implementation
- [ ] 1.1 …
  - Files: `src/...`
  - Steps: …
- [ ] 1.2 …
  - Files: `tests/...`
  - Steps: …

## 2. Verification
- [ ] 2.1 Automated checks (`uv run pytest -q`, lint)
- [ ] 2.2 Manual scenario — …

## 3. Follow-up
- [ ] 3.1 Docs / changelog
- [ ] 3.2 Stakeholder comms
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
