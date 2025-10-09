---
description: Translate an approved idea into plan and tasks
argument-hint: {"change_id":"<slug>","project":"<slug>"}
---

# `/plan` — Stage 2: Blueprint

`/plan` converts `spec.md` into a working blueprint and task list packed with research notes, file paths, and pseudo-steps. The output lives inside the same change folder as `/ideate` and prepares `/work` to execute confidently.

## Objectives

1. Summarize the solution approach, scope boundaries, and key milestones in `plan.md` (including research findings).
2. Generate a sequenced checklist in `tasks.md` with sub-bullets for files, pseudo-code, and verification commands.
3. Identify affected capabilities and create delta spec skeletons under `specs/`.

## Workflow

1. **Gather Inputs**
   - Confirm `spec.md` reflects ≥95 % confidence.
   - Enumerate impacted systems/capabilities and run `rg`/`git grep` to log existing entry points (files + functions).
   - Capture supporting docs or specs; prep Context7 queries (library/topic/tokens) if available.

2. **Plan Structure**
   - Update `plan.md` with sections:
     - `## Summary` — restate problem, outcome, confidence.
     - `## Research & Discovery` — document search results, code paths, Context7 outputs.
     - `## Change Outline` — highlight modules/files with pseudo-steps or short code snippets when helpful.
     - `## Tests & Validation` — automated commands and manual scenarios.
     - `## Risks & Mitigations`, `## Follow-ups` — owners and sequencing.
   - Include fenced code blocks or pseudo snippets for complex logic.

3. **Task Breakdown**
   - Replace the scaffold with ordered checklist items (`- [ ] 1.1 …`).
   - Add sub-bullets for each task detailing files to edit, pseudo-steps, and verification commands (`uv run pytest -q`, manual checks, etc.).
   - Include discovery tasks (audits, dependency review) before implementation steps and mark optional parallel tracks as `[P]`.

4. **Spec Deltas**
   - For each capability, create or update `.flow-maestro/projects/<project>/changes/<change-id>/specs/<capability>/spec.md` using OpenSpec-style headers (`## ADDED`, `## MODIFIED`, etc.).
   - Keep deltas focused on behaviour changes and reference the plan/tasks where relevant.

5. **Log Progress**
   - Append a `plan` entry to `timeline.jsonl` summarizing scope, research highlights, owners, and next command.

## Output Templates

`plan.md`

```markdown
# Implementation Plan

## Summary
- Problem: …
- Desired outcome: …
- Confidence: …

## Research & Discovery
- Code search: `rg auth_provider`
- Existing flow: `src/app/auth.py:login_handler`
- Context7 (optional): library/topic/tokens

## Change Outline
- Update `src/app/auth.py` — add provider registry (pseudo-code)
- Adjust `templates/login.html` — new button state

## Tests & Validation
- Automated: `uv run pytest -q`, `npm run lint`
- Manual: sign-in with new provider, fallback scenario

## Risks & Mitigations
- Risk → Mitigation/owner

## Follow-ups
- Docs, announcements, monitoring
```

`tasks.md`

```markdown
## 0. Discovery
- [ ] 0.1 Audit current login flow
  - Files: `src/app/auth.py`, `templates/login.html`
  - Findings: …
- [ ] 0.2 Context capture
  - Docs/specs: …
  - Context7 request (optional): library/topic/tokens

## 1. Implementation
- [ ] 1.1 Add provider registry
  - Files: `src/app/auth.py`
  - Steps: create enum, inject into handler
- [ ] 1.2 Update template
  - Files: `templates/login.html`
  - Steps: add button, feature flag
- [ ] 1.3 Extend tests
  - Files: `tests/auth/test_login.py`
  - Assertions: success + failure

## 2. Verification
- [ ] 2.1 Automated checks (`uv run pytest -q`, `npm run lint`)
- [ ] 2.2 Manual scenario — sign-in via provider, rollback path

## 3. Follow-up
- [ ] 3.1 Update README / docs
- [ ] 3.2 Notify stakeholders
```

## Validation Checklist

- [ ] `spec.md` acknowledged and referenced
- [ ] `plan.md` updated with research, change outline, verification
- [ ] `tasks.md` sequenced with sub-bullets for files/steps/tests
- [ ] Delta specs created/updated for every affected capability
- [ ] Context7 or external research captured (if used)
- [ ] Timeline updated with planning summary

**Next**: `/work` to execute the checklist and capture progress notes.
