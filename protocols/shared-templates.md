---
title: Shared Strategos Templates
description: Reusable snippets aligned with the Strategos Prime workflow
---

# Shared Strategos Templates

> Used primarily by `/progress`, `/qa`, and `/seal` to keep the Evidence Ledger and reporting artifacts aligned with Strategos phases.

## Confidence Checklist (6 Criteria)

Use this after every Phase review. Confidence gates require meeting all six criteria (6/6 = 100% confidence); anything less pauses advancement until remediated.

- ✅ **Success Criteria Clarity** — Acceptance tests measurable (`path:line`).
- ✅ **Integration Points Documented** — Up/downstream touchpoints cited.
- ✅ **Pattern Consistency Verified** — Existing implementations referenced.
- ✅ **Risk Mitigation Planned** — Hazards paired with mitigations or owners.
- ✅ **Sub-Issue Alignment Confirmed** — Parent/child scope reconciled.
- ✅ **Verification Plan Ready** — Automated + manual checks defined.

> Read-only environments must note `cursor pending (read-only env)` instead of writing `.flow-maestro/cursor.json`.

## Evidence Ledger Snippet

Embed this table in planning outputs, work logs, or completion notes.

```markdown
## Evidence Ledger
| Type | Detail | Source |
| ---- | ------ | ------ |
| Observation | Existing deploy command uses `uv run flowm` | `README.md#Development` |
| Risk | Legacy script fails on macOS (needs validation) | UNKNOWN |
| Dependency | Requires secrets from Vault path `ops/flow` | External |
| Decision | Follow logging pattern in `src/flowm_cli/logger.py:18` | `src/flowm_cli/logger.py:18` |
```

## Work Log Update Skeleton (Phase IV)

```markdown
## Work Log Update - YYYY-MM-DD HH:MM - (Agent)

**Phase Focus**: <I/II/III/IV>
**Status**: Current state

**Evidence Additions**:
- Observation: … (`path:line`)

**Actions**:
- Key work since last log

**Findings / Decisions**:
- Risks surfaced, mitigations chosen

**Blockers**:
- Note if any; otherwise "None"

**Next Steps**:
- Planned follow-up work

**Posted to Linear**: ISSUE-ID (timestamp)
```

> Keep logs ≤600 tokens; link to detailed artifacts rather than embedding diffs. Render quickly with `uv run python scripts/autopost.py progress-log --set timestamp=...`.

## Final Completion Summary Skeleton (Phase IV)

```markdown
## Final Completion Summary

**Implemented**:
- …

**Verification**:
- Lint: PASS/FAIL (evidence)
- Test: PASS/FAIL (command)
- Build: PASS/FAIL
- Manual QA: Result + scenario

**Confidence**: 100% (6/6 criteria)
- Notes per criterion referencing evidence

**Artifacts**:
- PR/Commit links, dashboards, runbooks

**Risks & Follow-ups**:
- Outstanding items or tracked issues

**Handoff**:
- Ownership transfer instructions
```

## Context Review Summary (Phase II)

```markdown
## Context Review Summary — YYYY-MM-DD HH:MM

**Mission Decode**:
- Objective + constraints

**Recon Highlights**:
- Key Observations (ledger references)

**Risks / Unknowns**:
- Item → Mitigation / Owner

**Confidence**: <value> (criteria list)

**Next Phase**: Masterplan Forging / Additional Recon
```

---

Reference `protocols/strategos-prime.md` for the full doctrine and phase expectations. Macro renderers live in `templates/linear-macros/`; call `scripts/autopost.py` to populate them before posting.
