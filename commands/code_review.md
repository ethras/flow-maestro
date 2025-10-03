# `/code_review` Command

## Purpose
Review code changes for security, correctness, performance, and pattern consistency before completion.

## Signature
```
/code_review {"issue":{"id":"<issue-id>"},"context":{"modified_files":["file1.ts","file2.tsx"],"description":"..."}}
```

**Parameters**:
- `issue.id` (required): Linear issue identifier
- `context` (required): Review context
  - `modified_files`: List of files changed
  - `description`: Brief description of changes (optional)

## What This Command Does

1. **Assesses Review Scope**
   - Trivial: ≤3 files, <100 lines
   - Moderate: 4-10 files, 100-500 lines
   - Major: >10 files, >500 lines, or architectural changes

2. **Checks for Existing Review**
   - Validates if current review exists
   - Checks if review covers current change set
   - Verifies no unresolved 🔴 issues

3. **Performs Code Review**
   - Loads and examines each modified file
   - Checks against review checklist
   - Identifies issues by severity (🔴/🟡/🟢)

4. **Posts Review to Linear**
   - Formats findings by severity
   - Includes file references and line numbers
   - Provides actionable recommendations

5. **Updates State**
   - Records review completion
   - Updates cursor in `.flow-maestro/cursor.json`

## Expected Output

```markdown
# Code Review: JWT Token Service Implementation

## Summary
Reviewed JWT token generation service implementation. Code is functionally correct and follows existing patterns. Found one critical security issue and two warnings that should be addressed.

**Task Context**: Based on Linear issue FM-123 requirements
**Files Reviewed**: 
- src/services/JWTService.ts
- src/middleware/auth.middleware.ts
- tests/unit/JWTService.test.ts

**Scope**: Moderate (3 files, 220 LOC)

## 🔴 Critical Issues (1)

### 1. Hardcoded Secret Key
**File**: src/services/JWTService.ts:15-20
**Issue**: JWT secret key is hardcoded in source code
**Impact**: Security vulnerability - secret exposed in version control
**Fix**: Move to environment variable
```typescript
// Current (WRONG):
const SECRET_KEY = "my-secret-key-12345";

// Should be:
const SECRET_KEY = process.env.JWT_SECRET_KEY;
if (!SECRET_KEY) throw new Error("JWT_SECRET_KEY not configured");
```
**Existing Pattern**: See src/config/env.ts:30-40 for env var pattern

## 🟡 Warnings (2)

### 1. Missing Error Handling
**File**: src/services/JWTService.ts:45-52
**Issue**: Token verification can throw but error not handled
**Impact**: Application crashes when invalid token provided
**Existing Pattern**: See src/services/AuthService.ts:60-70 for error handling pattern

### 2. No Token Expiry Validation
**File**: src/middleware/auth.middleware.ts:25
**Issue**: Middleware doesn't validate token expiry before use
**Impact**: Expired tokens might be accepted
**Fix**: Add expiry check before processing token

## 🟢 Notes (1)

### 1. Different Caching Approach
**File**: src/services/JWTService.ts:80
**Note**: Uses Redis for token cache while similar code uses in-memory cache
**Not a Problem**: Both work correctly, Redis is better for distributed systems
**Implementation Note**: Aligns with task specification for scalability

## Verdict

**Status**: ❌ BLOCKED - Critical issue must be resolved

**Required Actions**:
1. Fix 🔴 Critical Issue #1 (hardcoded secret)
2. Address 🟡 Warning #1 (error handling)
3. Address 🟡 Warning #2 (expiry validation)

**Posted to Linear**: FM-123 (2024-01-15 15:00)

**Recommended next command**: `/logging` (fix critical issues) then `/code_review` (re-review)
```

## Review Checklist

### 🔴 Critical (Blocks Deployment)

**Security Issues**:
- Exposed secrets/credentials
- Unvalidated user input
- Missing authentication/authorization checks
- Injection vulnerabilities (SQL, command, etc.)
- Path traversal risks
- Cross-site scripting (XSS)

**Correctness Issues**:
- Logic errors that produce wrong results
- Missing error handling that causes crashes
- Race conditions
- Data corruption risks
- Broken API contracts
- Infinite loops or recursion

### 🟡 Warning (Should Address)

**Reliability Issues**:
- Unhandled edge cases
- Resource leaks (memory, file handles, connections)
- Missing timeout handling
- Inadequate logging for debugging
- Missing rollback/recovery logic

**Performance Issues**:
- Database queries in loops (N+1)
- Unbounded memory growth
- Blocking I/O where async is expected
- Missing database indexes for queries

**Inconsistency Issues**:
- Deviates from established project patterns
- Different error handling than rest of codebase
- Inconsistent data validation approaches

### 🟢 Notes (Optional)

- Alternative approaches used elsewhere in codebase
- Documentation that might help future developers
- Test cases that might be worth adding
- Configuration that might need updating

## When Code Review Can Be Skipped

**Optional** (all must be true):
- [ ] Only documentation or formatting files changed (no executable code or tests)
- [ ] No runtime-impacting configuration or dependency updates
- [ ] No security-sensitive areas touched (auth, data access, secrets)

If all boxes checked, skip review and note in completion summary:
```markdown
**Code Review**: Skipped (documentation/formatting-only changes)
```

**Required** (any true):
- Executable code or tests modified
- Runtime configuration, feature flags, or dependencies updated
- Security-sensitive logic or architectural changes introduced
- Prior review flagged unresolved 🔴 issues

## Existing Review Check

Before drafting new review, check for existing review:

**Criteria** (all must be satisfied to reuse):
1. **Temporal**: Review timestamp later than latest commit
2. **Scope Coverage**: Review lists every file in current change set
3. **Resolution Status**: No unresolved 🔴 Critical Issues
4. **Scope Stability**: No new files added, no re-review requests

**Action**:
- If all criteria pass: Reference prior review, skip duplicate
- If any fails: Perform and post new review

## Related Protocols
- `code-review.md` - Detailed code review protocol
- `task-completion.md` - Integration with completion workflow

## Examples

```bash
# Review code changes
/code_review {"issue":{"id":"FM-123"},"context":{"modified_files":["src/services/JWTService.ts","src/middleware/auth.middleware.ts","tests/unit/JWTService.test.ts"],"description":"JWT token service implementation"}}

# Review with minimal context (will infer from git)
/code_review {"issue":{"id":"FM-123"},"context":{}}
```

## State Updates

After `/code_review`, `.flow-maestro/cursor.json` is updated:

```json
{
  "issue_id": "FM-123",
  "mode": "code_review",
  "last_comment_cursor": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-15T15:05:00Z",
  "reviews_done": false
}
```

After all 🔴 issues resolved:

```json
{
  "issue_id": "FM-123",
  "mode": "code_review",
  "last_comment_cursor": "2024-01-15T16:00:00Z",
  "updated_at": "2024-01-15T16:05:00Z",
  "reviews_done": true
}
```

