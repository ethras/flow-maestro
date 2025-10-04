---
description: Capture a raw idea, validate intent, and prepare inputs for planning
argument-hint: {"idea":{"title":"<working-title>","context":"<brief>"}}
---

# `/ideate` — Stage 0: Idea Intake

Use this command when a new initiative surfaces. The goal is to transform a raw idea into a mission brief ready for `/plan`.

## Objectives

1. Clarify the problem, stakeholders, and desired impact.
2. Identify constraints, success signals, and compatibility with existing protocols.
3. Establish a preliminary Evidence Ledger scaffold.

## Workflow

1. **Context Sweep**
   - Gather existing docs, tickets, or chat transcripts.
   - Note who owns the idea, target users, and deadlines.

2. **Mission Draft**
   - Capture working title, elevator pitch, success criteria, and hard constraints.
   - Document unanswered questions as `UNKNOWN` entries with proposed research paths.
   - Seed the Evidence Ledger using the shared table template (`protocols/shared-templates.md`).

3. **Risk Scan**
   - Brainstorm obvious hazards (compliance, data migration, staffing, sequencing).
   - Mark each risk with likelihood/impact and potential owners.

4. **Planning Hand-off**
   - Summarize outcome (<150 tokens) to feed directly into `/plan` Phase I.
   - Store artifacts in `.flow-maestro/workbench/` (create if missing) or attach to the relevant Linear discussion for shared access.

## Output Skeleton

```markdown
## Idea Intake — YYYY-MM-DD HH:MM

**Problem Statement**: …
**Stakeholders**: …
**Desired Impact**: …

**Preliminary Success Signals**:
- …

**Constraints**:
- …

**Evidence Ledger Starter**:
| Type | Detail | Source |
| ---- | ------ | ------ |
| Observation | … | … |
| Risk | … | … |
| Dependency | … | … |
| UNKNOWN | … | … |

**Initial Risks**:
- Risk → Mitigation owner

**UNKNOWN**:
- Question → Research plan

**Ready for**: `/plan`
```

## Validation Checklist

- [ ] Stakeholders identified
- [ ] Success signals captured
- [ ] Constraints enumerated
- [ ] Risks + UNKNOWN items recorded
- [ ] Summary prepared for `/plan`

**Next**: `/plan` to engage Strategos Prime.
