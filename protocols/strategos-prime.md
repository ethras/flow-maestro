# Strategos Prime — File-First Edition

Strategos Prime now operates entirely on local state. Each change folder moves through four disciplined phases with checkpoints that map to the CLI commands.

## Phase I — Ideation (`/ideate`)
- Clarify problem, users, and success signals.
- Capture constraints and `[NEEDS CLARIFICATION]` markers in `spec.md`.
- Confidence target: ≥95 % before moving forward.

## Phase II — Blueprint (`/plan`)
- Translate the spec into `plan.md` and `tasks.md`.
- Identify affected capabilities and draft delta specs.
- Gate: verification plan documented, risks assigned.

## Phase III — Execution (`/work`)
- Work strictly from `tasks.md` in order.
- Journal progress and decisions in `notes/` and timeline entries.
- Keep delta specs synchronized with implementation reality.

## Phase IV — Quality (`/qa` + `flowm specs apply`)
- Run automated and manual verification; log results in `qa.md`.
- Validate delta specs, then apply them to canonical specs.
- Archive the change after successful merge.

### Confidence Criteria
1. Success criteria measurable and in `spec.md`.
2. Dependencies called out in `plan.md`.
3. Implementation pattern documented (`plan.md` + journal).
4. Risks tracked with owners.
5. Delta specs ready to merge (validated).
6. Verification complete with reproducible commands.

All six criteria must hold before spec deltas are applied.

### Flow Maestro Etiquette
- **Single Source**: `.flow-maestro/projects/<project>/specs/` is truth. Changes live under `changes/` until merged.
- **Traceability**: Reference files as `path:line` in journals, plans, and QA notes.
- **Small Batches**: Prefer changes that can reach `/qa` within a day. Split initiatives if needed.
- **Archive Discipline**: `flowm specs apply` moves the change to `changes/archive/`; never edit archived folders except for audits.
