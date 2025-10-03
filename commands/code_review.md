---
description: Review code changes for security, correctness, and quality
argument-hint: {"issue":{"id":"<issue-id>"},"context":{...}}
---

# `/code_review` — Code Review

## Linear MCP Workflow

1. **Check Existing Review**: `list_comments_linear(issueId: "<issue-id>")`
   - Look for recent code review
   - Verify it covers current changes
   - Check for unresolved 🔴 issues

2. **Perform Review**: Examine modified files
   - Check against review checklist (see below)
   - Identify issues by severity: �� Critical / 🟡 Warning / 🟢 Note

3. **Post Review**: `create_comment_linear(issueId: "<issue-id>", body: "<review>")`
   - Format findings by severity
   - Include file references, line numbers
   - Provide actionable recommendations

4. **Update State**: Write cursor to `.flow-maestro/cursor.json`
   - If the environment is read-only, explicitly note "cursor pending (read-only env)" in your review output instead

---

## Review Checklist

### 🔴 Critical (Blocks Deployment)
- **Security**: Exposed secrets, unvalidated input, injection vulnerabilities
- **Correctness**: Logic errors, missing error handling, race conditions, data corruption

### 🟡 Warning (Should Address)
- **Reliability**: Unhandled edge cases, resource leaks, missing timeouts
- **Performance**: N+1 queries, unbounded memory, blocking I/O
- **Inconsistency**: Deviates from project patterns

### 🟢 Note (Optional)
- Alternative approaches, documentation, test suggestions

---

## Expected Output

```markdown
# Code Review: JWT Token Service

**Files Reviewed**: 
- src/services/JWTService.ts
- src/middleware/auth.middleware.ts
- tests/unit/JWTService.test.ts

**Scope**: Moderate (3 files, 220 LOC)

## 🔴 Critical Issues (1)

### 1. Hardcoded Secret Key
**File**: src/services/JWTService.ts:15-20
**Issue**: JWT secret hardcoded in source
**Fix**: Move to environment variable
**Pattern**: See src/config/env.ts:30-40

## 🟡 Warnings (2)

### 1. Missing Error Handling
**File**: src/services/JWTService.ts:45-52
**Pattern**: See src/services/AuthService.ts:60-70

### 2. No Token Expiry Validation
**File**: src/middleware/auth.middleware.ts:25

## Verdict

**Status**: ❌ BLOCKED - Fix 🔴 Critical Issue #1

**Posted to Linear**: FM-123 (2024-01-15 15:00)

**Next**: `/logging` (fix issues) then `/code_review` (re-review)
```

---

## When to Skip Review

**Optional** (all must be true):
- [ ] Only docs/formatting changed (no code/tests)
- [ ] No runtime config/dependency updates
- [ ] No security-sensitive areas touched

**Required** (any true):
- Executable code or tests modified
- Config, feature flags, dependencies updated
- Security-sensitive logic changed
- Prior review has unresolved 🔴 issues

---

## Confidence Assessment After Review

Re-calculate confidence with review results (see `protocols/shared-templates.md` for the checklist):

```markdown
**Confidence Assessment**: 100% (6/6 criteria)
1. ✅ Success Criteria: Met
2. ✅ Integration Points: Documented
3. ✅ Pattern Consistency: Verified in review
4. ✅ Risk Mitigation: Security review passed
5. ✅ Sub-Issue Alignment: N/A
6. ✅ Verification Plan: Tests pass

**Next**: `/completion`
```

---

## Next Command Logic

- **All 🔴 resolved, 🟡 addressed**: `/completion`
- **🔴 Critical issues found**: `/logging` (fix) → `/code_review` (re-review)
- **🟡 Warnings only**: Decision to fix or accept, then `/completion`

---

## Reference

- **Protocols**: `protocols/sub-issue-governance.md`
- **Linear MCP**: `list_comments_linear`, `create_comment_linear`
- **State**: `.flow-maestro/cursor.json` (`reviews_done: true` when passed)
