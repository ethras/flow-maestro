---
title: Shared Linear Comment Templates
description: Reusable snippets for Flow Maestro commands
---

# Shared Comment Templates

## Confidence Checklist
- ✅ Success Criteria Clarity (cite Linear evidence)
- ✅ Integration Points Documented
- ✅ Pattern Consistency Verified
- ✅ Risk Mitigation Planned
- ✅ Sub-Issue Alignment Confirmed
- ✅ Verification Plan Ready

> Use this checklist whenever a command asks you to report confidence. If the environment is read-only, note "cursor pending (read-only env)" instead of attempting to update `.flow-maestro/cursor.json`.

## Final Completion Summary Skeleton
```
## Final Completion Summary

**Implemented**:
- Item

**Verification**:
- Lint: PASS
- Test: PASS
- Build: PASS

**Code Review**:
- Reviewer | Date | Outcome

**Artifacts**:
- PR/Commit references

**Risks/Follow-ups**:
- Outstanding items or tracked issues

**Handoff**: Next steps or owner
```

> Reference this template from completion workflows instead of embedding copies in multiple commands.

## Work Log Update Skeleton
```
## Work Log Update - YYYY-MM-DD HH:MM - (Agent)

**Status**: Current state

**Actions**:
- Key work since last update

**Findings**:
- Discoveries, decisions, or measurements

**Blockers**:
- Note if any; otherwise "None"

**Next Steps**:
- Planned follow-up work

**Posted to Linear**: ISSUE-ID (timestamp)
```

> Keep the work log under 600 tokens; link to detailed artifacts rather than duplicating large diffs.
