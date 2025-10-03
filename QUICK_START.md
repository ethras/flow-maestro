# Flow Maestro Commands - Quick Start Guide

## Installation

1. **Install System Prompt**

   ```
   Read flow-maestro/SYSTEM_PROMPT.md
   Install it as your highest-precedence System role prompt
   ```

2. **Verify Linear MCP Access**

   ```
   Ensure Linear MCP is configured and accessible
   Test with a simple Linear query
   ```

3. **Run Onboarding**
   ```
   /onboarding
   ```

## Basic Workflow

### 1. Start Work on an Issue

```bash
/startup {"issue":{"id":"FM-123"}}
```

**Output**: Mission summary, context status, confidence assessment, next command recommendation

### 2. Log Progress

```bash
/logging {"issue":{"id":"FM-123"},"observations":{"status":"Implementing feature","actions":"Created service class","findings":"None","blockers":"None","next_steps":"Add unit tests"}}
```

**Output**: Work log posted to Linear, parent notification decision, next command recommendation

### 3. Review Code

```bash
/code_review {"issue":{"id":"FM-123"},"context":{"modified_files":["src/service.ts","tests/service.test.ts"]}}
```

**Output**: Review findings by severity, verdict, next command recommendation

### 4. Complete Issue

```bash
/completion {"issue":{"id":"FM-123"},"summary":"Feature implemented and tested"}
```

**Output**: Completion summary posted to Linear, status updated, next command recommendation

## Parent/Child Workflow

### Working with Parent Issues

```bash
# Start parent issue
/startup {"issue":{"id":"FM-100"}}

# Output enumerates all sub-issues
# Select child to work on

# Start child issue
/startup {"issue":{"id":"FM-101"}}

# Work on child...
/logging {"issue":{"id":"FM-101"},"observations":{...}}

# Complete child
/completion {"issue":{"id":"FM-101"}}

# Repeat for all children

# Complete parent (after all children terminal)
/completion {"issue":{"id":"FM-100"}}
```

## Command Reference

| Command          | Purpose              | When to Use                  |
| ---------------- | -------------------- | ---------------------------- |
| `/onboarding`    | Setup and verify     | Once per environment         |
| `/startup`       | Start work on issue  | First time working on issue  |
| `/resume`        | Resume work on issue | Returning to issue           |
| `/logging`       | Log work progress    | During implementation        |
| `/code_review`   | Review code changes  | Before completion            |
| `/completion`    | Complete issue       | After all work done          |
| `/task_creation` | Create new tasks     | For follow-ups or sub-issues |

## Confidence Thresholds

- **<67% (≤4/6)**: 🛑 HALT - Ask user for clarification
- **83% (5/6)**: ⚠️ STOP - Present options, await approval
- **≥95% (6/6)**: ✅ PROCEED - Implement autonomously

## Quality Gates

Before `/completion`:

- ✅ Lint: PASS (or documented override)
- ✅ Test: PASS (or documented override)
- ✅ Build: PASS (or documented override)
- ✅ Code Review: Done (no unresolved 🔴)
- ✅ Logging: Final work log posted

## Common Patterns

### Pattern 1: Simple Feature Implementation

```bash
/startup {"issue":{"id":"FM-123"}}
# Implement feature...
/logging {"issue":{"id":"FM-123"},"observations":{...}}
# Continue implementation...
/logging {"issue":{"id":"FM-123"},"observations":{...}}
/code_review {"issue":{"id":"FM-123"},"context":{...}}
# Fix any issues found...
/completion {"issue":{"id":"FM-123"}}
```

### Pattern 2: Epic with Sub-Issues

```bash
# Create parent
/task_creation {"task_details":{"title":"Feature Epic",...}}

# Create children
/task_creation {"task_details":{"title":"Child 1","parent_id":"FM-100",...}}
/task_creation {"task_details":{"title":"Child 2","parent_id":"FM-100",...}}

# Work on each child
/startup {"issue":{"id":"FM-101"}}
# ... implement, log, review, complete

/startup {"issue":{"id":"FM-102"}}
# ... implement, log, review, complete

# Complete parent
/completion {"issue":{"id":"FM-100"}}
```

### Pattern 3: Blocked Issue

```bash
/startup {"issue":{"id":"FM-123"}}
# Discover blocker...
/logging {"issue":{"id":"FM-123"},"observations":{"blockers":"Waiting on API deployment",...}}
# If child issue, notify parent
# Wait for blocker resolution
/resume {"issue":{"id":"FM-123"}}
# Continue work...
```

## File Structure

```
.flow-maestro/
└── cursor.json                        # Workflow state

flow-maestro/
├── README.md                          # Overview
├── SYSTEM_PROMPT.md                   # System prompt (install this!)
├── QUICK_START.md                     # This file
├── MCP_VS_COMMANDS.md                 # MCP vs Commands comparison
├── IMPLEMENTATION_SUMMARY.md          # Implementation summary
│
├── commands/                          # Slash commands (copied to projects)
│   ├── onboarding.md                  # /onboarding
│   ├── startup.md                     # /startup
│   ├── resume.md                      # /resume
│   ├── logging.md                     # /logging
│   ├── code_review.md                 # /code_review
│   ├── completion.md                  # /completion
│   └── task_creation.md               # /task_creation
│
├── protocols/                         # Reference protocols (centralized)
│   ├── universal-agent.md             # Core principles
│   ├── sub-issue-governance.md        # Parent/child rules
│   ├── parent-child-information-flow.md  # Info flow
│   └── universal-task-template.md     # Task template
│
└── templates/                         # PRP templates (centralized)
    └── prp-templates/
        ├── prp-template.md
        └── create-prp-guide.md
```

## Tips

1. **Always end with next command**: Every response should recommend the next command
2. **Use confidence gates**: Don't proceed with <95% confidence
3. **Parent/child discipline**: Always startup child before implementation
4. **Quality gates**: Run lint/test/build before completion
5. **Document decisions**: Keep Linear comments updated with rationale

## Troubleshooting

### "Confidence too low"

- Run `/context_gathering` to research missing information
- Ask user for clarification via ClarificationProtocol
- Don't proceed until confidence ≥95%

### "Parent completion blocked"

- Verify all children are in terminal states (completed/canceled)
- Complete remaining children individually
- Retry parent completion

### "Code review failed"

- Fix all 🔴 critical issues
- Address 🟡 warnings
- Re-run `/code_review`
- Only proceed to `/completion` after review passes

## Next Steps

1. Read `SYSTEM_PROMPT.md` thoroughly
2. Install it as System prompt
3. Run `/onboarding`
4. Start with `/startup {"issue":{"id":"YOUR-ISSUE-ID"}}`
5. Follow the recommended next commands

## Support

- **Slash Commands**: See `commands/` for command documentation
- **Protocols**: See `protocols/` for reference protocols
- **PRP Templates**: See `templates/prp-templates/` for PRP templates
- **Examples**: See `README.md` for more examples
