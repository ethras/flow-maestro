---
description: Kick off or re-sync execution on a Linear issue using Strategos artifacts
argument-hint: {"issue":{"id":"<issue-id>","mode":"start|resume"}}
---

# `/launch` — Stage 3: Execution Kickoff

Use `/launch` at the start of active work on an issue or when returning after a pause. It aligns the team with Strategos artifacts and validates readiness.

## Modes

- `mode: "start"` (default) — First time engaging the issue.
- `mode: "resume"` — Re-entry after interruption; focuses on deltas.

## Workflow

1. **Fetch Issue**: `get_issue_linear(id: "<issue-id>")`
   - Confirm title, priority, parent links match Strategos blueprint.
   - Note success criteria and constraints in the Evidence Ledger.

2. **Comment Audit**: `list_comments_linear(issueId: "<issue-id>")`
   - Review oldest → newest for manifests, decisions, risks.
   - Append new observations to the ledger with comment timestamps.

3. **Recon Delta**
   - Compare repository state against Strategos Recon notes (`rg`, `tree`, quick scripts).
   - Record changes or UNKNOWN items back into the ledger.

4. **Status Alignment**
   - If `mode = start`, call `update_issue_linear(..., state: "In Progress")` unless parent/ownership rules forbid it.
   - If `mode = resume`, validate state is still correct; adjust only if misaligned.

5. **Confidence Gate**
   - Apply the 6-criteria checklist (`protocols/shared-templates.md`).
   - Require ≥95% before moving to implementation. Otherwise, return to `/plan` or `/blueprint` to close gaps.

6. **Cursor Update**
   - Write `.flow-maestro/cursor.json` (or log "cursor pending (read-only env)").

## Output Skeleton

```markdown
## Launch: FM-123 — YYYY-MM-DD HH:MM

**Mode**: start
**Evidence Ledger Delta**:
- Observation: … (`src/...:line`)
- Risk: … (comment 2025-10-03 14:02)
- UNKNOWN: … → Owner …

**Comment Audit**:
- 2025-10-02 18:10 — Context Manifest updated, requires using AuthConfig v3
- 2025-10-03 12:45 — Security sign-off pending

**Confidence**: 100% (6/6 criteria)

**Next**: `/progress {"issue":{"id":"FM-123"}}`
```

## Parent/Child Guidance

- **Child Issues**: Pull parent constraints into the ledger; cite siblings where integration is required.
- **Parent Issues**: Enumerate children (`list_issues_linear(parentId: …)`), record status, and coordinate rather than implement.

## Validation Checklist

- [ ] Issue + comment data inspected and logged
- [ ] Strategos artifacts cross-referenced
- [ ] Confidence ≥95% documented
- [ ] Cursor updated / read-only noted

**Next**: `/progress` for ongoing execution logs.

