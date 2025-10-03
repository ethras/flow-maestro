# Flow Maestro — Command-Based Workflow System

**Intent**: Mirror the exact Flow Maestro MCP workflow using slash commands instead of MCP tools.

## Overview

- **Purpose**: Orchestrate Linear-centered workflows via slash commands
- **No Dependencies**: No server, no MCP, no NestJS, no SurrealDB
- **State**: File-based cursor in `.flow-maestro/cursor.json`
- **Integration**: Direct Linear MCP access (agents call Linear directly)
- **Protocols**: Same markdown protocols as MCP variant, different transport

## Commands

- `/onboarding` - Install system prompt and confirm Linear access
- `/startup {"issue":{"id":"<string>"}}` - Start work on an issue
- `/resume {"issue":{"id":"<string>"}}` - Resume work on an issue
- `/logging {"issue":{"id":"<string>"},"observations":{...}}` - Log work progress
- `/code_review {"issue":{"id":"<string>"},"context":{...}}` - Review code changes
- `/completion {"issue":{"id":"<string>"},"summary":"<optional>"}` - Complete an issue
- `/task_creation {"issue":{"id":"<string>"},"task_details":{...}}` - Create new tasks

## Directory Structure

```
flow-maestro/
├── README.md                              # This file
├── SYSTEM_PROMPT.md                       # System prompt for agents
├── QUICK_START.md                         # Quick start guide
├── MCP_VS_COMMANDS.md                     # MCP vs Commands comparison
├── IMPLEMENTATION_SUMMARY.md              # Implementation summary
│
├── commands/                              # Slash commands (copied to projects)
│   ├── onboarding.md                      # /onboarding - Setup & verification
│   ├── startup.md                         # /startup - Start work on issue
│   ├── resume.md                          # /resume - Resume work on issue
│   ├── logging.md                         # /logging - Log work progress
│   ├── code_review.md                     # /code_review - Review code changes
│   ├── completion.md                      # /completion - Complete issue
│   └── task_creation.md                   # /task_creation - Create new tasks
│
├── protocols/                             # Reference protocols (centralized)
│   ├── universal-agent.md                 # Core agent principles
│   ├── sub-issue-governance.md            # Parent/child workflow rules
│   ├── parent-child-information-flow.md   # Parent/child information flow
│   └── universal-task-template.md         # Universal task template
│
└── templates/                             # PRP templates (centralized)
    └── prp-templates/
        ├── prp-template.md
        └── create-prp-guide.md
```

## State Management

The system uses a simple file-based cursor stored in `.flow-maestro/cursor.json`:

```json
{
  "issue_id": "FM-123",
  "mode": "logging",
  "last_comment_cursor": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T15:00:00Z"
}
```

This cursor tracks:

- Current issue being worked on
- Current workflow mode
- Last comment read (for delta reads)
- Last update timestamp

## Execution Loop

1. `/onboarding` → install system prompt, confirm Linear access
2. `/startup` on target issue (or `/resume` if returning)
3. `/logging` as work progresses
4. `/code_review` before completion (when applicable)
5. `/completion` to close
6. `/task_creation` for follow-ups

Always propose the next command at the end of each response.

## Confidence & Approval Gates (95% Rule)

Score across 6 criteria:

1. Success Criteria Clarity
2. Integration Points Documented
3. Pattern Consistency
4. Risk Mitigation
5. Sub-Issue Alignment
6. Verification Plan

**Thresholds**:

- <67% (≤4/6): HALT. Ask targeted questions. No implementation.
- 83% (5/6): STOP for critical decisions. Present options, await approval.
- ≥95% (6/6): Proceed, document decisions in Linear.

## Parent–Child Information Flow

- **Parent → Child**: Before child work, run `/startup` on the child and carry parent context down
- **Child → Parent**: On major decisions/completion, post a concise summary back to the parent with links
- **Parent is for orchestration**; implementation details live in children
- Each sub-issue requires its own `/startup` before implementation

## Quality Gates & Documentation

- Lint/test/build (as applicable) before declaring completion; link evidence
- Keep a Decision Log in Linear: what/why for key choices
- Post structured outputs to Linear comments (snapshot, review findings, completion note)
- Use concise bullets; include links to PRs/commits/artifacts

## Getting Started

1. Read `SYSTEM_PROMPT.md` and install it as your highest-precedence System prompt
2. Ensure Linear MCP access is configured
3. Run `/onboarding` to confirm setup
4. Start working with `/startup {"issue":{"id":"YOUR-ISSUE-ID"}}`

## Key Differences from MCP Variant

| Aspect        | MCP Variant          | Command Variant             |
| ------------- | -------------------- | --------------------------- |
| Transport     | MCP tools            | Slash commands              |
| Server        | NestJS + SurrealDB   | None (file-based)           |
| State         | SurrealDB cursor     | `.flow-maestro/cursor.json` |
| Linear Access | Server calls Linear  | Agent calls Linear directly |
| Protocols     | Server-provided      | File-based templates        |
| Handshake     | Tool call → response | Command → agent interprets  |

## Commands vs Protocols

**Slash Commands** (`commands/` - copied to each project):

- `onboarding.md` - `/onboarding` - Setup and verification
- `startup.md` - `/startup` - Start work on issue
- `resume.md` - `/resume` - Resume work on issue
- `logging.md` - `/logging` - Log work progress
- `code_review.md` - `/code_review` - Review code changes
- `completion.md` - `/completion` - Complete issue
- `task_creation.md` - `/task_creation` - Create new tasks

**Reference Protocols** (`protocols/` - centralized, not copied):

- `universal-agent.md` - Core agent principles and operating rules
- `sub-issue-governance.md` - Parent/child workflow rules
- `parent-child-information-flow.md` - Parent/child information flow guidance
- `universal-task-template.md` - Universal task template

**Distribution Model**:

- Commands are copied to each project via CLI tool (e.g., to `.flow-maestro/commands/`)
- Protocols remain centralized in the flow-maestro repository for reference

## Examples

```bash
# Start work on an issue
/startup {"issue":{"id":"FM-123"}}

# Log progress
/logging {"issue":{"id":"FM-123"},"observations":{"status":"Investigating","blockers":"Waiting on PR #42"}}

# Complete the issue
/completion {"issue":{"id":"FM-123"},"summary":"Feature delivered; tests and CI passed"}
```

## Support

For questions or issues, refer to:

- `SYSTEM_PROMPT.md` for agent operating instructions
- `commands/` for slash command documentation
- `protocols/` for reference protocols
- `templates/prp-templates/` for PRP templates
