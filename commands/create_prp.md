---
description: Draft a PRP using the Flow Maestro template and MCP workflow
argument-hint: (no arguments)
---

# `/create_prp` — Create Product Requirements Proposal

## Purpose

Create a Flow Maestro-ready PRP that an implementing agent can execute in a single pass. The command centralizes the former `templates/prp-templates/create-prp-guide.md` guidance and walks you through using the canonical template at `templates/prp-templates/prp-template.md`.

## Prerequisites

- Ensure Flow Maestro assets live under `.flow-maestro/` (see `/onboarding`).
- Confirm the feature or issue context you are documenting.
- Have `templates/prp-templates/prp-template.md` open as your working canvas.

## Workflow

1. **Copy the PRP Template**
   - Create a new file under `work/prps/` (e.g., `work/prps/<feature>-prp.md`).
   - Paste the contents of `templates/prp-templates/prp-template.md` as your starting point.

2. **Run Context Gathering**
   - Use codebase search (`rg`, existing MCP context gathering) to locate patterns, tests, and configuration relevant to the feature.
   - Document file paths, functions, and patterns you expect the executor to follow.

3. **Perform External Research (Optional)**
   - When library knowledge is incomplete, query Context7.
   - Record authoritative URLs (with section anchors) and critical insights in the template’s YAML block.

4. **Populate Template Sections**
   - **Goal & Why**: Define the measurable outcome, deliverable, and success definition. Capture business value and dependencies.
   - **What & Success Criteria**: Describe expected behaviour and list box-checked acceptance criteria.
   - **All Needed Context**: Fill the YAML snippet with must-read documentation, repo files, and any Context7 configuration.
   - **Current vs Desired Structure**: Outline relevant portions of the existing tree and how it will evolve.
   - **Known Gotchas**: Call out framework quirks, environment requirements, and traps discovered during research.
   - **Implementation Blueprint**: Convert findings into dependency-ordered tasks, patterns, and integration notes.
   - **Validation Loop**: Specify lint/test/build commands that must pass and any manual QA steps.
   - **Final Checklist**: Ensure the bottom validation checkboxes reflect the success gates.

5. **Assess Confidence**
   - Apply the 6-criteria confidence rubric from `/onboarding` (Success Criteria, Integration Points, Pattern Consistency, Risk Mitigation, Sub-Issue Alignment, Verification Plan).
   - The PRP must support ≥95% confidence before completion.

6. **Save & Register**
   - Save under `work/prps/` with a descriptive filename.
   - When workflow tooling requires, call the MCP `create_prp` tool with `draft_status: "ready"` and link the saved file.

## Research Standards

- Investigate related components, routes, database models, and tests before writing guidance.
- Document conventions (naming, folder placements, coding patterns) with concrete references.
- Capture validation and quality gates already enforced in the project (e.g., lint, type-check, unit tests).
- When referencing files, provide precise paths and highlight the pattern to replicate.

## Information Density Requirements

- Every reference must be actionable: include anchors, line hints, or reason-to-read notes.
- Prefer pattern examples already in the repo over prose descriptions.
- Specify command invocations exactly as they should be executed by the implementing agent.
- Avoid duplicate content from the template; enrich each section with situational context.

## Completion Checklist

- [ ] Template sections populated with specific, verifiable instructions.
- [ ] YAML block lists authoritative docs and code references.
- [ ] Implementation tasks are dependency ordered and reference existing patterns.
- [ ] Validation commands cover lint/test/build plus manual QA as needed.
- [ ] Confidence ≥95% per the 6-criteria rubric.

## Next Command Logic

- **Need tasks created**: `/task_creation`
- **Ready for execution**: Provide PRP to implementing agent, then `/startup` on the relevant issue.
- **Further research required**: Continue context gathering before finalizing the PRP.
