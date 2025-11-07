# PRP Template v4 - Flow Maestro MCP Integration

**Feature**: [Feature Name]

---

## Goal

**Feature Goal**: [Specific, measurable end state of what needs to be built]

**Deliverable**: [Concrete artifact - React component, API route, integration, etc.]

**Success Definition**: [How you'll know this is complete and working]

## User Persona (if applicable)

**Target User**: [Specific user type - developer, end user, admin, etc.]

**Use Case**: [Primary scenario when this feature will be used]

**User Journey**: [Step-by-step flow of how user interacts with this feature]

**Pain Points Addressed**: [Specific user frustrations this feature solves]

## Why

- [Business value and user impact]
- [Integration with existing features]
- [Problems this solves and for whom]

## What

[User-visible behavior and technical requirements]

### Success Criteria

- [ ] [Specific measurable outcomes]

## All Needed Context

### Context Completeness Check

_Before writing this PRP, validate: "If someone knew nothing about this codebase, would they have everything needed to implement this successfully?"_

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- url: [Complete URL with section anchor]
  why: [Specific methods/concepts needed for implementation]
  critical: [Key insights that prevent common implementation errors]

- file: [exact/path/to/pattern/file.tsx]
  why: [Specific pattern to follow - component structure, hook usage, etc.]
  pattern: [Brief description of what pattern to extract]
  gotcha: [Known constraints or limitations to avoid]

# Flow Maestro Change State
- instruction: "Capture blueprint output in .flow-maestro/projects/<project>/changes/<change-id>/plan.md and tasks.md."
- note: "Create or update delta specs in specs/<capability>/spec.md so `flowm specs apply` can merge them."

<!-- CONTEXT7_BLOCK_START -->
# Context7 MCP Integration (for complex tasks)
context7_config:
  libraryName: "[Library Name]"  # e.g., "Next.js", "React"
  topic: "[Focused Topic]"       # e.g., "routing", "hooks"
  tokens: 2000                    # Token budget allocation
<!-- CONTEXT7_BLOCK_END -->
```

### Current Codebase Structure

```bash
# Run `tree` in the root of the project to get an overview
[Insert current codebase tree here]
```

### Desired Codebase Structure

```bash
# Files to be added and their responsibilities
[Insert desired structure with new files]
```

### Known Gotchas & Library Quirks

```typescript
// CRITICAL: [Library name] requires [specific setup]
// Example: Next.js 15 App Router - Route handlers must export named functions
// Example: 'use client' directive must be at top of file, affects entire component tree
// Example: Server Components can't use browser APIs or event handlers
// Example: We use TypeScript strict mode and require proper typing
```

## Implementation Blueprint

### Data Models and Structure

Create the core data models to ensure type safety and consistency.

```typescript
// Examples:
// - Zod schemas for validation
// - TypeScript interfaces/types
// - Database schema types
// - API response types
// - Component prop types
```

### Implementation Tasks (ordered by dependencies)

```yaml
Task 1: CREATE [path/to/file.ts]
  - IMPLEMENT: [What to build]
  - FOLLOW pattern: [existing/file/path.ts] ([specific pattern to follow])
  - NAMING: [Naming conventions to follow]
  - PLACEMENT: [Where to place the file]
  - DEPENDENCIES: [Previous tasks this depends on]

Task 2: CREATE [path/to/component.tsx]
  - IMPLEMENT: [Component description]
  - FOLLOW pattern: [existing/component/path.tsx] ([component structure, props typing])
  - NAMING: [Component naming conventions]
  - DEPENDENCIES: [Import types from Task 1]
  - PLACEMENT: [Component directory structure]

# Continue with additional tasks...
```

### Implementation Patterns & Key Details

```typescript
// Show critical patterns and gotchas - keep concise, focus on non-obvious details

// Example: Component pattern
interface [Domain]Props {
  // PATTERN: Strict TypeScript interfaces
  data: [Domain]Data;
  onAction?: (id: string) => void;
}

export function [Domain]Component({ data, onAction }: [Domain]Props) {
  // PATTERN: Client/Server component patterns
  // GOTCHA: 'use client' needed for event handlers, useState, useEffect
  // CRITICAL: Server Components for data fetching, Client Components for interactivity

  return (
    // PATTERN: Consistent styling approach
    <div className="existing-class-pattern">
      {/* Follow existing component composition patterns */}
    </div>
  );
}

// Example: API route pattern
export async function GET(request: Request): Promise<Response> {
  // PATTERN: Request validation and error handling
  // GOTCHA: [TypeScript-specific constraint or framework requirement]
  // RETURN: Response object with proper TypeScript typing
}
```

### Integration Points

```yaml
DATABASE:
  - migration: "Add table 'feature_data' with proper indexes"
  - client: "@/lib/database/client"
  - pattern: "createClient() for client components, createServerClient() for server components"

CONFIG:
  - add to: .env.local
  - pattern: "NEXT_PUBLIC_* for client-side env vars"
  - pattern: "FEATURE_TIMEOUT = process.env.FEATURE_TIMEOUT || '30000'"

ROUTES:
  - file structure: app/feature-name/page.tsx
  - api routes: app/api/feature-name/route.ts
  - middleware: middleware.ts (root level)
```

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Run after each file creation - fix before proceeding
npm run lint                    # ESLint checks with TypeScript rules
npx tsc --noEmit               # TypeScript type checking (no JS output)
npm run format                 # Prettier formatting

# Project-wide validation
npm run lint:fix               # Auto-fix linting issues
npm run type-check             # Full TypeScript validation

# Expected: Zero errors. If errors exist, READ output and fix before proceeding.
```

### Level 2: Unit Tests (Component Validation)

```bash
# Test each component/hook as it's created
npm test -- __tests__/[domain].test.tsx
npm test -- __tests__/use[Hook].test.ts

# Full test suite for affected areas
npm test -- components/[domain]/
npm test -- hooks/

# Coverage validation (if available)
npm test -- --coverage --watchAll=false

# Expected: All tests pass. If failing, debug root cause and fix implementation.
```

### Level 3: Integration Testing (System Validation)

```bash
# Development server validation
npm run dev &
sleep 5  # Allow startup time

# Page load validation
curl -I http://localhost:3000/[feature-page]
# Expected: 200 OK response

# API endpoint validation
curl -X POST http://localhost:3000/api/[resource] \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  | jq .  # Pretty print JSON response

# Production build validation
npm run build
# Expected: Successful build with no TypeScript errors or warnings
```

## Final Validation Checklist

### Technical Validation

- [ ] All validation levels completed successfully
- [ ] All tests pass: `npm test`
- [ ] No linting errors: `npm run lint`
- [ ] No type errors: `npx tsc --noEmit`
- [ ] No formatting issues: `npm run format --check`
- [ ] Production build succeeds: `npm run build`

### Feature Validation

- [ ] All success criteria from "What" section met
- [ ] Manual testing successful: [specific commands from Level 3]
- [ ] Error cases handled gracefully with proper TypeScript error types
- [ ] Integration points work as specified
- [ ] User persona requirements satisfied (if applicable)

### Code Quality Validation

- [ ] Follows existing patterns and naming conventions
- [ ] File placement matches desired codebase tree structure
- [ ] Anti-patterns avoided
- [ ] Dependencies properly managed with correct TypeScript typings
- [ ] Configuration changes properly integrated

---

## Anti-Patterns to Avoid

- ❌ Don't create new patterns when existing ones work
- ❌ Don't skip validation because "it should work"
- ❌ Don't ignore failing tests - fix them
- ❌ Don't hardcode values that should be config
- ❌ Don't catch all exceptions - be specific
