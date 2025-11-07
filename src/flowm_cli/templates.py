"""Reusable Markdown templates for Flow Maestro assets."""
from __future__ import annotations

import textwrap

SPEC_TEMPLATE = textwrap.dedent(
    """\
# Change: {change_id}

## Overview
- Problem summary: <describe the gap or opportunity>
- Impacted users or teams: <list primary audiences>
- Business context: <why this matters now>

## Core Features
- Feature concept: <behaviour change in one sentence>
- Supporting capabilities: <list high-level behaviours>
- Out of scope: <call out exclusions>

## Data Model & Storage (no code)
- Entities & relationships: <describe tables/types and key fields>
- Source of truth: <systems responsible for each data set>
- Compliance & retention notes: <policies or constraints>

## Workflow & States
- Lifecycle: <outline status transitions and triggers>
- Roles & permissions: <who can act when>
- Edge cases: <highlight recovery paths>

## API & Integration Notes (no code)
- Backend modules/services: <describe repositories, resolvers, services>
- External integrations: <Frankfurter, Azure, etc. — include data flow>
- Observability: <logging/metrics expectations>

## Web Experience Overview
- Screens & components: <layout, states, interactions>
- Accessibility/performance: <considerations>
- Error handling: <how issues surface to users>

## Mobile Experience Overview
- Screens & flows: <camera, AI sheet, status views>
- Offline/latency handling: <how the app behaves>
- Platform nuances: <iOS/Android specifics>

## Dependencies & Assumptions
- Dependency: <service/library> — Assumption: <availability/performance>
- Chronology: <critical milestones or launch sequencing>

## Technical Decisions
- Decision: <choice> - Rationale: <why>
- Trade-offs: <impact on future work>

## Risks & Mitigations
- Risk: <issue> - Mitigation: <contingency>

## Environment Variables
- Env var: <VARIABLE_NAME>=<purpose and owner>

## Open Questions
- [NEEDS CLARIFICATION: <question or assumption>]

## Success Criteria
- Success signal: <how we'll measure success>
"""
).strip()

PLAN_FILENAME = "plan.md"
LEGACY_BLUEPRINT_FILENAME = "blueprint.md"

CONSTITUTION_TEMPLATE = textwrap.dedent(
    """\
# Project Constitution — {project_slug}

## Core Architecture
- Title: <behavior/invariant>
  - Summary: <1-2 sentences the whole team should know>
  - Source: <change-id/path:line>
  - Last verified: <YYYY-MM-DD>

## Data & Integrations
- Title: <API/schema contract>
  - Summary: <constraints, auth, rate limits>
  - Source: <change-id/path:line>
  - Last verified: <YYYY-MM-DD>

## Operational Guardrails
- Title: <runbook/flag/rollback rule>
  - Summary: <what to do / avoid>
  - Source: <change-id/path:line>
  - Last verified: <YYYY-MM-DD>

## Risks & Mitigations
- Title: <recurring risk>
  - Summary: <impact + mitigation>
  - Source: <change-id/path:line>
  - Last verified: <YYYY-MM-DD>

## Watchlist
- Title: <open truth we are tracking>
  - Summary: <why it matters>
  - Owner: <team or person>
  - Source: <change-id/path:line>
  - Last reviewed: <YYYY-MM-DD>
"""
).strip()

PLAN_TEMPLATE = textwrap.dedent(
    """\
# Implementation Plan

## Summary
- Problem: <one sentence recap>
- Desired outcome: <target state>
- Confidence: <risk level or blockers>

## Research & Discovery
- Code search highlights: <files, commands, references>
- Existing flows to audit: <entry points>
- External references: <docs, tickets, context>

## Implementation Phases
- Phase 1: <focus and owner>
- Phase 2: <follow-on work>

## Tests & Validation
- Automated: <commands to run>
- Manual: <scenarios or sign-off steps>

## Risks & Mitigations
- Risk: <issue> - Mitigation: <contingency>

## Follow-ups
- <documentation, rollout, comms, telemetry>
"""
).strip()

TASKS_TEMPLATE = textwrap.dedent(
    """\
## Phase 0 - Discovery
- [ ] 0.1 Capture baseline context in `notes/research.md`
  - Summary: <link relevant findings>
- [ ] 0.2 Align scope and constraints
  - Notes: <stakeholders or decisions>

## Phase 1 - Implementation
- [ ] 1.1 Primary change track
  - Targets: <files or modules>
  - Verification: <quick checks during build>
- [ ] 1.2 Extend or add tests
  - Targets: <test paths>
  - Assertions: <behaviour to prove>

## Phase 2 - Verification
- [ ] 2.1 Automated validation (`uv run pytest -q`, linters)
- [ ] 2.2 Manual scenario walkthrough
  - Steps: <user journey or edge cases>

## Phase 3 - Follow-up
- [ ] 3.1 Documentation or changelog updates
- [ ] 3.2 Notify stakeholders / handoff
"""
).strip()

PLACEHOLDER_PATTERNS = {
    "<describe the gap or opportunity>": "spec overview placeholder",
    "<list primary audiences>": "spec overview placeholder",
    "<why this matters now>": "spec overview placeholder",
    "<behaviour change in one sentence>": "core feature placeholder",
    "<list high-level behaviours>": "core feature placeholder",
    "<call out exclusions>": "core feature placeholder",
    "<describe tables/types and key fields>": "data model placeholder",
    "<systems responsible for each data set>": "data model placeholder",
    "<policies or constraints>": "data model placeholder",
    "<outline status transitions and triggers>": "workflow placeholder",
    "<who can act when>": "workflow placeholder",
    "<highlight recovery paths>": "workflow placeholder",
    "<describe repositories, resolvers, services>": "api placeholder",
    "<Frankfurter, Azure, etc. — include data flow>": "api placeholder",
    "<logging/metrics expectations>": "api placeholder",
    "<layout, states, interactions>": "web placeholder",
    "<considerations>": "web placeholder",
    "<how issues surface to users>": "web placeholder",
    "<camera, AI sheet, status views>": "mobile placeholder",
    "<how the app behaves>": "mobile placeholder",
    "<iOS/Android specifics>": "mobile placeholder",
    "<service/library>": "dependency placeholder",
    "<availability/performance>": "dependency placeholder",
    "<critical milestones or launch sequencing>": "dependency placeholder",
    "<APIs, schemas, events>": "data and interface placeholder",
    "<systems, services, or boundaries>": "architecture placeholder",
    "<choice>": "decision placeholder",
    "<why>": "decision rationale placeholder",
    "<VARIABLE_NAME>": "environment variable placeholder",
    "<purpose and owner>": "environment variable placeholder",
    "<question or assumption>": "open question placeholder",
    "<how we'll measure success>": "success criteria placeholder",
    "<one sentence recap>": "blueprint summary placeholder",
    "<target state>": "blueprint summary placeholder",
    "<risk level or blockers>": "blueprint summary placeholder",
    "<files, commands, references>": "research placeholder",
    "<entry points>": "research placeholder",
    "<docs, tickets, context>": "research placeholder",
    "<focus and owner>": "phase blueprint placeholder",
    "<follow-on work>": "phase blueprint placeholder",
    "<commands to run>": "validation placeholder",
    "<scenarios or sign-off steps>": "validation placeholder",
    "<issue>": "risk placeholder",
    "<contingency>": "risk placeholder",
    "<documentation, rollout, comms, telemetry>": "follow-up placeholder",
    "<link relevant findings>": "discovery placeholder",
    "<stakeholders or decisions>": "discovery placeholder",
    "<files or modules>": "implementation placeholder",
    "<quick checks during build>": "implementation placeholder",
    "<test paths>": "implementation placeholder",
    "<behaviour to prove>": "implementation placeholder",
    "<user journey or edge cases>": "verification placeholder",
}

__all__ = [
    "SPEC_TEMPLATE",
    "PLAN_FILENAME",
    "LEGACY_BLUEPRINT_FILENAME",
    "CONSTITUTION_TEMPLATE",
    "PLAN_TEMPLATE",
    "TASKS_TEMPLATE",
    "PLACEHOLDER_PATTERNS",
]
