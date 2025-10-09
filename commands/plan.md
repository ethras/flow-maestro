---
description: Translate an approved idea into plan and tasks
argument-hint: {"change_id":"<slug>","project":"<slug>"}
---

# `/plan` — Stage 2: Blueprint

`/plan` converts `spec.md` into a working blueprint and task list. The output lives inside the same change folder as `/ideate` and prepares `/work` to execute confidently.

## Objectives

1. Summarize the solution approach, scope boundaries, and key milestones in `plan.md`.
2. Generate a sequenced checklist in `tasks.md` with owners or hints.
3. Identify affected capabilities and create delta spec skeletons under `specs/`.

## Workflow

1. **Gather Inputs**
   - Confirm `spec.md` reflects ≥95 % confidence.
   - Enumerate impacted systems and capabilities.

2. **Plan Structure**
   - Update `plan.md` with sections:
     - `## Goals`
     - `## Approach`
     - `## Dependencies`
     - `## Risks`
     - `## Verification`
   - Call out constraints, sequencing, and fallback strategies.

3. **Task Breakdown**
   - Replace the scaffolded entries in `tasks.md` with ordered checklist items (`- [ ] 1.1 …`).
   - Label optional parallel tracks as `[P]` where applicable.

4. **Spec Deltas**
   - For each capability, create or update `.flow-maestro/projects/<project>/changes/<change-id>/specs/<capability>/spec.md` using OpenSpec-style headers (`## ADDED`, `## MODIFIED`, etc.).
   - Keep deltas focused on the requirements that change.

5. **Log Progress**
   - Append a `plan` entry to `timeline.jsonl` summarizing scope, owners, and next command.

## Output Templates

`plan.md`

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
- `uv run pytest -q`
- Manual spot checks
```

`tasks.md`

```markdown
## 1. Implementation
- [ ] 1.1 Update API contract
- [ ] 1.2 Implement handler
- [ ] 1.3 Write integration tests

## 2. Follow-up
- [ ] 2.1 Update docs
- [ ] 2.2 Notify stakeholders
```

## Validation Checklist

- [ ] `spec.md` acknowledged and referenced
- [ ] `plan.md` updated with approach, dependencies, verification
- [ ] `tasks.md` sequenced with clear outcomes
- [ ] Delta specs created/updated for every affected capability
- [ ] Timeline updated with planning summary

**Next**: `/work` to execute the checklist and capture progress notes.
