---
description: Translate the Strategos master plan into PRPs and Linear issues
argument-hint: {"mission":{"id":"<optional-parent-id>"}}
---

# `/blueprint` — Stage 2: Delivery Architecture

Apply this command after `/plan` to produce execution-ready assets: Product Requirement Proposals (PRPs), child issues, and verification scaffolding.

## Inputs

- Strategos artifacts: Mission Decode, Evidence Ledger, Master Plan, Final Briefing.
- Idea intake notes from `/ideate`.
- Any stakeholder approvals gathered during planning.

## Workflow

1. **Evidence Ledger Sync**
   - Copy relevant ledger entries into your working document.
   - Confirm citations, update UNKNOWN items, and add owners.

2. **PRP Drafting (Optional but Recommended)**
   - Start from `templates/prp-templates/prp-template.md`.
   - Populate sections using Strategos phases and ledger references.
   - Capture external research under `external_docs` with URLs.

3. **Issue Blueprinting**
   - For each Strategos phase, decide whether to create a parent issue with children or a single task.
   - Use the strategic phase breakdown to populate the universal template (`protocols/universal-task-template.md`).
   - Keep responses ≤600 tokens; link to repositories or PRP for depth.

4. **Linear Issue Creation**
   - Call `create_issue_linear` with populated template.
   - Post the Evidence Ledger snippet as the first comment for traceability.
   - Record relationships (parent/child, dependencies) and note them in the ledger.

5. **Verification Wiring**
   - Document automated tests (`uv run pytest …`), manual QA, and monitoring expectations.
   - Create follow-up tickets for gaps (e.g., data migration, security review).

## Output Skeleton

```markdown
## Blueprint Summary — YYYY-MM-DD HH:MM

**Issues Created**:
- FM-124 — Phase A: … (child of FM-120)
- FM-125 — Phase B: …

**Evidence Ledger Snapshot**:
- Observation: … (`src/...:line`)
- Dependency: … (External)
- Risk: … → Owner …
- UNKNOWN: … → Follow-up issue FM-126

**Verification Alignment**:
- Automated: `uv run pytest -q`
- Manual: …

**Next**: `/launch {"issue":{"id":"FM-124"}}`
```

## Validation Checklist

- [ ] Strategos artifacts incorporated (cited in issues/PRPs)
- [ ] Evidence Ledger updated after issue creation
- [ ] Linear hierarchy reflects Strategos phases
- [ ] Verification plan documented per issue
- [ ] Follow-up tasks logged for residual UNKNOWN items

**Next**: `/launch` to begin execution on the chosen issue.

