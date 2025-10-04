---
description: Perform evidence-backed code review with risk tracking
argument-hint: {"issue":{"id":"<issue-id>"}}
---

# `/review` — Stage 5: Quality Audit

Use `/review` once implementation reaches a checkpoint. The objective is to reduce residual risk and validate readiness for `/seal`.

## Strategos Alignment

- Operates in Phase IV (Final Seal).
- Record every finding in the Evidence Ledger with `path:line` references.

## Workflow

1. **Historical Scan**
   - `list_comments_linear(issueId: "<issue-id>")` for prior reviews and unresolved findings.
   - Note existing 🔴/🟡 items in the ledger.

2. **File Review**
   - Inspect modifications grouped by module/pattern.
   - Apply severity taxonomy:
     - 🔴 Critical — blocks deployment (security, correctness, data integrity)
     - 🟡 Warning — should address (reliability, performance, consistency)
     - 🟢 Note — optional improvements or documentation

3. **Record Findings**
   - Update the ledger per finding (`path:line`, severity, mitigation owner).
   - Cross-reference Strategos patterns to ensure consistency.

4. **Publish Review**
   - `create_comment_linear(issueId: "<issue-id>", body: "<review>")`
   - Structure comment by severity, include actionable fixes, and cite files.

5. **Cursor Update**
   - Reflect the latest review status in `.flow-maestro/cursor.json` (or note read-only).

## Output Skeleton

```markdown
# Review: JWT Token Service

**Scope**: Moderate (3 files, 220 LOC)
**Evidence Ledger Updates**:
- 🔴 Risk: Hardcoded secret (`src/services/JWTService.ts:15-20`) → Move to env var (owner: Alice)
- 🟡 Risk: Missing error handling (`src/services/JWTService.ts:45-52`)
- UNKNOWN: Performance impact pending benchmark

## 🔴 Critical (1)
1. Hardcoded Secret Key — Move to env var (`src/config/env.ts:30-40` pattern)

## 🟡 Warnings (2)
1. Missing Error Handling — Add guard clauses
2. Token Expiry Validation — Ensure middleware checks tokens

## Verdict
Status: ❌ BLOCKED — Resolve 🔴 Critical issue

**Next**: `/progress` (implement fixes) then `/review` (re-audit)
```

## Validation Checklist

- [ ] Ledger captures all findings with severity + owners
- [ ] Review comment posted to Linear with actionable guidance
- [ ] Confidence recalculated (≥95% to proceed)
- [ ] Cursor updated / read-only noted

**Next**: `/progress` for remediation or `/seal` if all findings cleared.

