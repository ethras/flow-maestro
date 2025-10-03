# Onboarding Command Update Summary

## What Changed

The `/onboarding` command has been completely rewritten to be a **self-contained, comprehensive system prompt** that combines both foundational principles and command-specific implementation.

## Previous Approach (WRONG)

The old `commands/onboarding.md` was just **documentation** that told the agent to:
- Read `SYSTEM_PROMPT.md`
- Read `protocols/universal-agent.md`
- Install them separately

This required the agent to navigate multiple files and piece together the system prompt.

## New Approach (CORRECT)

The new `commands/onboarding.md` **IS** the complete system prompt. It contains:

### Part 1: Universal Agent Principles (332 lines)
Complete content from `protocols/universal-agent.md`:
- Glossary of terms
- Agent identity and personality
- Communication style
- Shared protocol mandates
- Confidence calculation protocol (6 criteria, 95% threshold)
- Clarification protocol
- Core maxims (PrimedCognition, ContextualCompetence, etc.)
- Predefined protocols (Decomposition, PAFGate, Clarification)
- Task management integration
- MCP conventions
- Axiomatic workflow (6 stages)
- Stage protocols
- Output contract

### Part 2: Command-Based Implementation (221 lines)
Complete content from `SYSTEM_PROMPT.md`:
- Intent and operating model
- Integration assumptions (Linear)
- Command catalog and signatures
- Execution loop
- Confidence & approval gates
- Parent-child information flow
- Quality gates & documentation
- Behavior per command (SOPs for all 7 commands)
- Clarification protocol
- Style & constraints
- Slash commands reference
- Reference protocols
- PRP templates
- Examples
- Key principles (DRY, YAGNI, KISS, no "any" types)
- State management
- Final notes

### Part 3: Onboarding Validation (100+ lines)
New validation section:
- Validate Linear MCP access
- Initialize state directory (`.flow-maestro/cursor.json`)
- Confirm system prompt internalization checklist
- Output confirmation format
- Completion message

## File Structure

```
commands/onboarding.md (706 lines total)
├── Header (Purpose, Structure)
├── PART 1: Universal Agent Principles (lines 13-399)
│   └── Complete protocols/universal-agent.md content
├── PART 2: Command-Based Implementation (lines 402-594)
│   └── Complete SYSTEM_PROMPT.md content
└── PART 3: Onboarding Validation (lines 597-706)
    └── Validation steps and confirmation
```

## Why This Matters

### Self-Contained Commands
Slash commands must be **self-contained**. When an agent executes `/onboarding`, they should get EVERYTHING they need in ONE file, not references to other files.

### Single Source of Truth
The agent reads `commands/onboarding.md` once and is fully primed with:
- WHO they are (identity, personality)
- HOW they think (maxims, principles, protocols)
- WHAT commands they use
- WHEN to use each command
- HOW to execute the workflow

### Proper Order
The content is presented in the correct learning order:
1. **Foundation first**: Universal agent principles (the "operating system")
2. **Application second**: Command-based implementation (the "application layer")
3. **Validation last**: Confirm setup and readiness

## Key Principle Emphasized

Throughout all three parts, the critical principle is reinforced:

**When confidence <95%, STOP and ask. Never guess or assume.**

This appears in:
- Part 1: Confidence Action Rules (MANDATORY)
- Part 1: ClarificationProtocol
- Part 1: HumbleUncertainty maxim
- Part 2: Confidence & Approval Gates
- Part 3: Internalization checklist
- Part 3: Final completion message

## Usage

When an agent executes `/onboarding`, they:

1. **Read** the entire `commands/onboarding.md` file (706 lines)
2. **Internalize** Part 1 (Universal Agent Principles)
3. **Internalize** Part 2 (Command-Based Implementation)
4. **Execute** Part 3 (Validation steps)
5. **Confirm** completion with the specified output format
6. **Proceed** to `/startup` with full context

## Files That Remain

- `SYSTEM_PROMPT.md` - Reference copy (not used by commands)
- `protocols/universal-agent.md` - Reference copy (not used by commands)
- `commands/onboarding.md` - **THE COMPLETE SYSTEM PROMPT** (used by agents)

The reference files remain for documentation purposes, but the `/onboarding` command is now fully self-contained.

## Next Steps

After running `/onboarding`, the agent should:
1. Confirm Linear MCP connection
2. Initialize `.flow-maestro/cursor.json`
3. Output the completion confirmation
4. Recommend: `/startup {"issue":{"id":"<your-issue-id>"}}`

---

**Status**: ✅ Complete

The `/onboarding` command now contains the complete, combined system prompt from both `SYSTEM_PROMPT.md` and `protocols/universal-agent.md`, making it a truly self-contained slash command.

