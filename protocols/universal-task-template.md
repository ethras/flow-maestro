---
title: Universal Task Template — Strategos Workflow
description: Evidence-led Linear issue template aligned to Strategos Prime phases
---

# Universal Task Template (Strategos Edition)

Use this template when creating or updating Linear issues. Each block maps to the Strategos Prime phases and enforces the Evidence Ledger discipline.

## Phase Mapping Overview

- **Phase I – Intelligence Summon** → `Observations`, `Key Findings`
- **Phase II – Deep Reconnaissance** → `Approach`, `Proposed File Changes`
- **Phase III – Masterplan Forging** → `Implementation Phases`, `Verification Plan`
- **Phase IV – Final Seal** → `Summary`, `Success Criteria`, `Risks`, `Dependencies`, `Next Actions`

## Planning-to-Template Guide

1. Populate the **Evidence Ledger** while running `/plan`, `/launch`, or `/progress` workflows.
2. Promote ledger insights into the sections below with explicit `path:line` citations.
3. Flag any `UNKNOWN` entries that block ≥95% confidence until resolved.

## Template Skeleton

```markdown
## Evidence Ledger (Phase I-II)
- Observation: <fact> (`path:line`)
- Risk: <hazard> (`path:line`)
- Dependency: <system/person> (`path:line` or External)
- UNKNOWN: <missing data>

## Mission Decode (Phase I)
- Objective: <primary outcome>
- Success Metrics: <quantified goals>
- Constraints: <time, compliance, tooling>

## Recon Summary (Phase II)
- Architecture Notes: <components, patterns>
- Analogues: <prior implementations>
- Tech Debt / Hazards: <legacy risks>

## Implementation Phases (Phase III)
1. **Phase Name** — Mission Goal
   - Tasks: Ordered tactical steps
   - Key Files: `path:line`
   - Validation: Tests/metrics to run
   - Risks: Mitigations or decision gates
   - Mermaid:
     ```mermaid
     flowchart TD
     ```

## Verification Plan (Phase III)
- Automated: `uv run pytest -q`, linters, builds
- Manual QA: Scenarios, environments, datasets
- Monitoring: Alerts, dashboards, metrics

## Summary (Phase IV)
One-sentence WHAT/WHY referencing ledger evidence.

## Success Criteria (Phase IV)
- [ ] Criterion 1 (measurable, cite evidence)
- [ ] Criterion 2
- [ ] Criterion 3

## Risks & Mitigations (Phase IV)
- Risk → Mitigation (`path:line` or External)
- UNKNOWN → Owner / Follow-up plan

## Dependencies & Coordination (Phase IV)
- Upstream: Issues, teams, releases
- Downstream: Consumers, documentation, runbooks

## Next Actions (Phase IV)
- Immediately after issue creation / completion
- Follow-up tasks (link to Linear IDs)

## Agent Notes
- Capabilities required, environment constraints, safety modes
- Cursor expectations (`.flow-maestro/cursor.json` handling)

## Context Manifest Hooks
- Link to latest Context Review Summary
- Reference prior Strategos plan artifacts
```

## Usage Notes

- Keep responses ≤600 tokens when copying into Linear; link to detailed artifacts instead of duplicating large diffs.
- Always include at least one mermaid diagram per implementation phase.
- Update the Evidence Ledger whenever new facts emerge; propagate updates to downstream sections.

## Validation Checklist

- [ ] Evidence Ledger populated with `path:line` references
- [ ] Mission Decode clarifies objectives and constraints
- [ ] Implementation phases dependency ordered with validation hooks
- [ ] Verification plan covers automated + manual checks
- [ ] Risks, dependencies, and next actions reflect current state
- [ ] Confidence ≥95% across the 6 criteria before handoff
