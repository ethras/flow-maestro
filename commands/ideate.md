---
description: Ask clarifying questions until the change spec feels locked in
argument-hint: {"change_id":"<slug>","project":"<slug>"}
---

# `/ideate` — Stage 1: Clarify the Change

Use `/ideate` to turn vague ideas into a confident proposal stored in `.flow-maestro/projects/<project>/changes/<change-id>/spec.md`.

## Objectives

1. Capture the core problem, desired impact, and success signals.
2. Identify open questions and assumptions, marking them clearly in the spec.
3. Reach ≥95 % confidence before handing off to `/plan`.

## Workflow

1. **Set Context**
   - Confirm the active project via `flowm projects use <slug>`.
   - Scaffold the change if it doesn’t exist: `flowm changes init <change-id> --project <slug>`.

2. **Spec Interview**
   - Ask clarifying questions until gaps are resolved.
   - Record answers in `spec.md` using sections:
     - `## Problem`
     - `## Desired Outcome`
     - `## Constraints`
     - `## Success Signals`
     - `## Open Questions`
   - Leave `[NEEDS CLARIFICATION: …]` markers where follow-up is required.

3. **Confidence Pass**
   - Check that success criteria are measurable.
   - Verify stakeholders, timelines, and scope boundaries are documented.
   - When confidence ≥95 %, remove remaining `[NEEDS CLARIFICATION]` markers and log the decision in `timeline.jsonl`.

## Spec Template

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

Store supplementary research in `notes/` or `assets/` inside the change folder.

## Validation Checklist

- [ ] Problem and outcome articulated in `spec.md`
- [ ] Constraints and success signals enumerated
- [ ] Stakeholders or owner documented
- [ ] Confidence ≥95 % (or remaining gaps noted)
- [ ] Timeline updated with latest summary

**Next**: `/plan` to translate the idea into an executable blueprint and task list.
