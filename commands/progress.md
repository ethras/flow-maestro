---
description: Record execution progress, ledger updates, and next actions
argument-hint: {"issue":{"id":"<issue-id>"},"scope":"delta|full","autopost":true}
---

# `/progress` — Stage 4: Execution Momentum

Use this command to document ongoing work, surface risks, and keep the Evidence Ledger current.

> **Autopost default**: `/progress` publishes the resulting log to Linear automatically. Opt out only when running analysis-only dry runs.

## Workflow

0. **Verify Linear Session**
   - `get_user_linear(query: "me")` to confirm authentication.
   - If unauthorized, set `cursor.pending_post = true` and request credentials before proceeding.

1. **Select Scope**
   - `scope: "delta"` (default) for updates within the last 24 hours.
   - `scope: "full"` when summarizing across multiple sessions or agents.

2. **Ledger Update**
   - Add new observations, decisions, or UNKNOWN items with `path:line` or comment timestamps.
   - Note risk mitigations, ownership changes, and integration impacts.

3. **Compose Progress Log**
   - Follow the Phase IV work-log template (`protocols/shared-templates.md`).
   - Include `Phase Focus` to highlight which Strategos phase advanced.

4. **Autopost Comment**
   - Unless `autopost` is explicitly `false`, agents **must** publish immediately after drafting.
   - Render via `uv run python scripts/autopost.py progress-log --set timestamp=... --set issue_key=FM-123 ...` (macros live in `templates/linear-macros/`).
   - Execute `create_comment_linear(issueId: "<issue-id>", body: "<log>")` and record the timestamp.
   - If autopost fails (network/auth), set `cursor.pending_post = true` and retry before closing the session.

5. **Parent Notifications**
   - Notify parents only for blockers, milestone completions, or cross-child impacts.
   - Use the short format from `protocols/parent-child-information-flow.md`.

6. **Cursor Update**
   - Write `.flow-maestro/cursor.json` with the latest comment metadata (`last_posted_at`, `pending_post` = false).
   - In read-only environments, log "cursor pending (read-only env); autopost required".

## Output Skeleton

```markdown
## Progress Log — 2025-10-04 14:30

**Phase Focus**: III → IV
**Status**: Implementation in progress

**Evidence Additions**:
- Observation: Added refresh flow (`src/auth/token_service.py:120`)
- Risk: Performance regression risk (UNKNOWN — pending benchmark)

**Actions**:
- Implemented JWT token generation service
- Added RS256 signing algorithm

**Findings / Decisions**:
- Integration with AuthMiddleware requires new adapter

**Blockers**: None

**Next Steps**:
- Benchmark refresh flow
- Update API documentation

**Posted to Linear**: FM-123 (2025-10-04 14:30)
**Autopost**: ✅ Immediate publish via helper script

**Next**: `/progress` (next session) or `/qa` (if code ready)
```

## Validation Checklist

- [ ] Evidence Ledger updated with new citations
- [ ] Scope declared (delta/full)
- [ ] Risks and UNKNOWN items routed to owners
- [ ] Linear comment posted (or `pending_post` documented with retry plan)
- [ ] Cursor updated / read-only noted

**Next**: `/qa` when changes are ready for audit, or `/progress` again for continued work.
