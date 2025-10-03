# `/logging` Command

## Purpose
Log work progress to Linear issue comments. Consolidates implementation work, decisions, and next steps.

## Signature
```
/logging {"issue":{"id":"<issue-id>"},"observations":{"status":"...","actions":"...","findings":"...","blockers":"...","next_steps":"..."}}`
```

**Parameters**:
- `issue.id` (required): Linear issue identifier
- `observations` (required): Work log details
  - `status`: Current work status
  - `actions`: Actions taken since last log
  - `findings`: Discoveries or issues found
  - `blockers`: Any blockers encountered
  - `next_steps`: Planned next steps

## What This Command Does

1. **Determines Log Scope**
   - Delta update (< 24h, same agent, no major changes)
   - Full log (≥ 24h, different agent, or major changes)

2. **Determines Parent vs Child Context**
   - Child issue: Log ALL implementation detail
   - Parent issue: Log ONLY coordination, reference children

3. **Posts Work Log to Linear**
   - Formats log using standard template
   - Includes timestamp and agent attribution
   - Updates Linear issue comments

4. **Evaluates Parent Notification** (for child issues)
   - Decides if parent needs notification
   - Posts parent notification if warranted

5. **Updates State**
   - Updates cursor in `.flow-maestro/cursor.json`
   - Records logging timestamp

## Expected Output

### Child Issue Logging (Implementation Detail)

```markdown
## Work Log Update - 2024-01-15 14:30 - (AI Agent)

#### Completed
- Implemented JWT token generation service
- Added unit tests for token validation
- Integrated with existing auth middleware

#### Decisions
- Chose RS256 over HS256 for better key rotation support
- Set token expiry to 15 minutes with 7-day refresh window
- Implemented token revocation list in Redis

#### Discovered
- Existing auth middleware needs update for JWT format
- Performance bottleneck in token validation (cached now)

#### Code Changes
- Added: src/services/JWTService.ts
- Modified: src/middleware/auth.middleware.ts
- Added: tests/unit/JWTService.test.ts

#### Next Steps
- Implement token refresh endpoint
- Update API documentation
- Run integration tests

**Posted to Linear**: FM-123 (2024-01-15 14:30)

**Parent Notification**: Not warranted (routine progress)

**Recommended next command**: `/logging` (continue work) or `/code_review` (if ready for review)
```

### Parent Issue Logging (Coordination Only)

```markdown
## Work Log Update - 2024-01-15 16:00 - (AI Agent)

#### Completed
- Coordinated authentication flow across 3 sub-issues
- Established shared AuthConfig interface
- See FM-101 (2024-01-15 14:30) for JWT implementation details
- See FM-102 (2024-01-15 15:15) for OAuth integration details

#### Decisions
- All auth components must use shared config interface
- Security review required before parent completion
- Integration tests will span all three components

#### Next Steps
- Resume FM-103 for session management implementation
- Schedule security review after all children complete

**Posted to Linear**: FM-100 (2024-01-15 16:00)

**Recommended next command**: `/startup {"issue":{"id":"FM-103"}}` (next child)
```

## Parent Notification Decision

After posting child work log, evaluate if parent notification is warranted:

**Post parent notification IF**:
- Log contains blockers requiring coordination
- Log indicates completion/major milestone
- Log contains decisions affecting siblings
- Log discovers integration impacts on other children
- Log changes assumptions from parent manifest

**Do NOT notify parent for**:
- Routine progress (implementation work without blockers/impacts)
- Minor bug fixes not affecting other children
- Code refactoring within child scope
- Normal quality gate execution

### Parent Notification Format

```markdown
## 🔗 Child Update: FM-102

**Event**: BLOCKER
**Timestamp**: 2024-01-15 15:30

**Summary**: OAuth provider API changed, endpoint /v2/oauth/authorize not available

**Impact**: FM-102 blocked, affects integration with FM-103 (session management depends on OAuth flow)

**Details**: See FM-102 (2024-01-15 15:30) for full blocker analysis and mitigation options

**Posted to Linear**: FM-100 (parent notification)

**Recommended next command**: `/resume {"issue":{"id":"FM-100"}}` (coordinate blocker resolution)
```

## Log Scope Decision

**Delta Update** (all must be true):
- Most recent Work Log < 24 hours old
- Same agent continues work
- No sub-issue status changes since last log
- No new blockers, critical decisions, or phase transitions
- Implementation phase unchanged

**Full Log** (any true):
- No Work Log exists or last log ≥ 24 hours old
- Different agent taking over
- Sub-issue status or scope changed
- New blocker, critical decision, or phase transition
- Implementation resumed after pause

## Work Log Template

```markdown
## Work Log Update - [YYYY-MM-DD HH:MM] - [Agent Attribution]

#### Completed
- [Action 1]
- [Action 2]

#### Decisions
- [Decision 1 with rationale]
- [Decision 2 with rationale]

#### Discovered
- [Finding 1]
- [Finding 2]

#### Code Changes
- Modified: [file path]
- Added: [file path]
- Updated: [file path]

#### Next Steps
- [Next action 1]
- [Next action 2]
```

## Transition to Code Review

**Trigger**: After logging implementation work and before attempting completion.

**Criteria**:
- Implementation for planned change set is complete
- Security-sensitive code, significant refactors, or architectural updates performed
- Task is about to move toward completion or handoff

**Action**:
- Post final Work Log entry summarizing completed work
- Invoke `/code_review` with modified files
- Resolve all 🔴 findings before proceeding to `/completion`

```markdown
**Implementation Complete**: All planned changes implemented

**Recommended next command**: `/code_review {"issue":{"id":"FM-123"},"context":{"modified_files":["src/services/JWTService.ts","src/middleware/auth.middleware.ts"]}}`
```

## Related Protocols
- `logging.md` - Detailed logging protocol
- `sub-issue-governance.md` - Parent vs child logging rules
- `parent-child-information-flow.md` - Parent notification guidance

## Examples

```bash
# Log work on child issue
/logging {"issue":{"id":"FM-123"},"observations":{"status":"Implementing JWT service","actions":"Created JWTService class, added unit tests","findings":"Auth middleware needs update","blockers":"None","next_steps":"Implement token refresh endpoint"}}

# Log coordination on parent issue
/logging {"issue":{"id":"FM-100"},"observations":{"status":"Coordinating sub-issues","actions":"Established shared AuthConfig interface","findings":"FM-102 blocked on OAuth API change","blockers":"FM-102 blocked","next_steps":"Escalate blocker to platform team"}}
```

## State Updates

After `/logging`, `.flow-maestro/cursor.json` is updated:

```json
{
  "issue_id": "FM-123",
  "mode": "logging",
  "last_comment_cursor": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T14:35:00Z"
}
```

