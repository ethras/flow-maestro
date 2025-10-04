<!-- Linear Issue Template: Universal Task Structure -->
**Priority**: [High/Medium/Low] | **Type**: [implement/fix/refactor/research/migrate/test/docs] | **Project**: [current-project]

### Planning-to-Template Guide
- **Observations → Summary/Context**: Lift concrete facts into Summary so reviewers understand the WHY without re-reading discovery notes.
- **Key Findings → Success Criteria/Risks**: Promote confirmed requirements into checked criteria; capture remaining concerns in Risks & Mitigations.
- **Approach → Impacted Modules & Data Contracts**: Describe planned touchpoints; cite module paths and API surfaces exactly as enumerated in the plan.
- **Proposed File Changes → Impacted Modules**: Mirror the file list verbatim, preserving justification so implementers stay aligned with precedent.
- **Verification Notes → Verification Plan**: Convert the checklist into lint/test/build targets and manual QA steps. If tooling coverage is missing, add TODOs before creating the issue.

## Observations
- Verified fact 1 (include repo paths, prior art, stakeholder notes)
- Verified fact 2

## Key Findings
- Gap/Risk 1 → Mitigation or owner
- Dependency/Decision awaiting confirmation

## Approach
- High-level step aligning with shared patterns
- Defensive consideration or fallback path

## Proposed File Changes
- `path/to/file.ext`: planned change and justification tied to Observations
- `another/file.ext`: planned change and rationale

## Verification Notes
- Automated: tests, lint, build targets
- Manual QA: environments, roles, datasets
- Open TODOs: follow-ups that require ownership

## Summary
One sentence WHAT and WHY.

## Success Criteria
- [ ] Criterion 1 (measurable)
- [ ] Criterion 2 (measurable)
- [ ] Criterion 3 (duplicate line as needed)

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
- Capabilities required: [technology stack from agent memory]
- Notes: [safety mode, test data, env]

## Context Manifest (to be populated during startup)
- Link to "Context Review Summary" comment

---
# Comment Snippets (Copy into Linear comments)

## Context Review Summary
- Existing context: [links/summary]
- Gaps identified: [list]
- Plan: [targeted research / proceed]

## Work Log Update - YYYY-MM-DD HH:MM - (Agent)
#### Completed
- …
#### Decisions
- …
#### Discovered
- …
#### Next Steps
- …

## Final Completion Summary
- Implemented: …
- Verification: [lint/test/build, manual QA]
- Risks/Follow-ups: …
- Artifacts/PR: [links]
