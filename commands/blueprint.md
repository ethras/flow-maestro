---
description: Translate an approved spec into blueprint and task breakdown
argument-hint: {"change_id":"<slug>","project":"<slug>"}
---

# `/blueprint` — Stage 2: Implementation Blueprint

`/blueprint` is a shortcut name for this `commands/blueprint.md` playbook. Mention the file path when directing humans or agents so they read the Markdown instead of expecting a slash command to execute. Running `/blueprint` updates `plan.md` (not `blueprint.md`) inside the change folder; the alias sticks for historical reasons, but the artifact we maintain is `plan.md`.

`/blueprint` converts `spec.md` into a detailed implementation plan and task list packed with research notes, file paths, pseudo-steps, and code samples. The output lives alongside `/ideate` in the change folder and prepares `/work` to execute confidently. Expect to spend meaningful time researching here—every question answered now is one less rediscovery during `/work`.

## Objectives

1. Summarize the solution approach, scope boundaries, and key milestones in `plan.md`, backed by concrete research findings logged during this phase.
2. Generate a sequenced checklist in `tasks.md` with sub-bullets for files, pseudo-code, commands, and verification steps.
3. Identify affected capabilities and create delta spec skeletons under `specs/`.

## Workflow

1. **Gather Inputs**
   - Confirm `spec.md` reflects ≥95 % confidence with narrative-only detail.
   - Run code searches (`rg`, `git grep`, Language Server peek) to locate entry points; capture the snippets you find.
   - Collect external knowledge (design docs, API references, RFCs) you’ll need later.

2. **Research Log (mandatory)**
   - Create `notes/research.md` (or append to the existing file) with dated sections summarizing findings.
   - Use all available channels: `flowm research capture` for git/code snapshots, Context7 queries for library docs, and web search when repo knowledge isn’t enough. Quote or paraphrase each result with links or cite-able identifiers so the next agent can act without repeating the lookup.
   - Highlight blockers, open questions, and follow-ups inline. Call out exactly which future task or plan section each finding supports (e.g., “feeds plan.md › Phases › Phase 2” or “unblocks tasks.md › 1.3”).
   - When screenshots or large outputs matter, link to artifacts stored under `notes/` or `assets/` and reference them from `plan.md`.
   - Promote reusable, cross-change insights into `.flow-maestro/projects/<project>/constitution.md` once you’ve validated them. Each entry needs a title, short summary, source (change/path:line), and “Last verified” date; keep speculative notes in `notes/` until they harden.

3. **Blueprint Structure**
   - Update `plan.md` with sections:
     - `## Summary` — restate problem, outcome, confidence.
     - `## Research & Discovery` — embed relevant excerpts from `notes/research.md`, including command outputs.
     - `## Implementation Phases` — outline numbered phases with goals, owners, affected packages/modules, and include pseudo-code or real code snippets.
     - `## Tests & Validation` — automated commands and manual scenarios.
     - `## Risks & Mitigations`, `## Follow-ups` — owners and sequencing.
   - Use fenced code blocks, pseudo-code, and command snippets to illustrate schema changes, GraphQL additions, or component structure.

5. **Task Breakdown**
   - Replace the scaffold in `tasks.md` with ordered checklist items (`- [ ] 1.1 …`).
   - Add sub-bullets detailing files to edit, pseudo-steps, and verification commands (`uv run pytest -q`, manual checks, etc.).
   - Include discovery tasks (audits, dependency review) before implementation steps and mark optional parallel tracks as `[P]`.
   - Embed code fences or command snippets where they clarify changes (migrations, component sketches, test commands).

6. **Spec Deltas**
   - For each capability, create or update `.flow-maestro/projects/<project>/changes/<change-id>/specs/<capability>/spec.md` using OpenSpec-style headers (`## ADDED`, `## MODIFIED`, etc.).
   - Tie delta narrative back to sections in `plan.md` or specific tasks.

7. **Log Progress**
   - Use `flowm timeline log --command blueprint "<scope + next command>"` to record research highlights, owners, and the next stage. Do not edit `timeline.jsonl` manually.

## Output Templates

`plan.md`

```markdown
# Implementation Blueprint

## Summary
- Problem: …
- Desired outcome: …
- Confidence: …

## Research & Discovery
- Search: `rg expenses`
- Existing flow: `apps/...`
- External refs: …

## Implementation Phases
- Phase 1 — Backend foundations (owner)
  - `apps/edgedb-api/.../expenses/*.ts`
  - ```edgeql
    # migration snippet
    ```
- Phase 2 — Web CRM (owner)
  - `apps/web/...`
  - ```tsx
    // component sketch
    ```

## Tests & Validation
- Automated: `uv run pytest -q`, `pnpm nx test ...`
- Manual: submit/approve/payment/PDF

## Risks & Mitigations
- Risk → Mitigation/owner

## Follow-ups
- Docs, rollout, monitoring
```

`tasks.md`

```markdown
## 0. Discovery
- [ ] 0.1 Audit current expense flow
  - Files: `apps/...`
  - Commands: `rg expense`
- [ ] 0.2 Capture env + policy decisions
  - Notes: optional receipts, FX freeze

## 1. Backend Foundations
- [ ] 1.1 Add EdgeDB schema & migration
  - Files: `dbschema/*.esdl`
  - Commands: `pnpm edgedb:migrate`
- [ ] 1.2 Build Nest module
  - Files: `apps/.../expenses/*.ts`
  - Code: ```ts
    // service outline
    ```

## 2. Verification
- [ ] 2.1 Automated checks (`uv run pytest -q`, `pnpm nx lint ...`)
- [ ] 2.2 Manual scenario — submit, approve, payment, export

## 3. Follow-up
- [ ] 3.1 Update README / docs
- [ ] 3.2 Notify finance ops
```

### Task-writing tips

- Keep each task focused on an outcome that fits inside a single working block (≤4 hours when possible).
- Add owners inline (`- [ ] 1.2 [@alex] ...`) and append `[P]` for steps that can run in parallel safely.
- Mark unresolved dependencies with `[BLOCKED: reason]` and capture the mitigation next to the task plus in `plan.md`.
- Update sub-bullets with actual file paths, commands, and code snippets as you learn; spawn a fresh change if brand-new scope appears.

## Validation Checklist

- [ ] `spec.md` acknowledged and referenced
- [ ] `plan.md` updated with research, phase outlines, and code snippets
- [ ] `tasks.md` sequenced with sub-bullets for files/steps/tests
- [ ] Delta specs created/updated for every affected capability
- [ ] Context7 or external research captured (if used)
- [ ] Timeline updated with blueprint summary

**Next**: `/work` to execute the checklist and capture progress notes.
