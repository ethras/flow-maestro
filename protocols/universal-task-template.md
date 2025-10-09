# Task Template — Change Execution

Use this lightweight template when expanding `tasks.md` during `/plan`. It keeps tasks small, sequenced, and verifiable.

```markdown
## 0. Discovery
- [ ] 0.1 Audit current behaviour
  - Files: `…`
  - Findings: …
- [ ] 0.2 Context capture
  - Docs/specs: …
  - Context7 request (optional): library/topic/tokens

## 1. Implementation
- [ ] 1.1 Describe concrete outcome (≤4 hours)
  - Files: `src/...`
  - Steps: …
- [ ] 1.2 …
  - Files: `tests/...`
  - Steps: …

## 2. Verification
- [ ] 2.1 Automated check (`uv run pytest -q`, lint)
- [ ] 2.2 Manual scenario (who + steps)

## 3. Follow-up
- [ ] 3.1 Documentation update
- [ ] 3.2 Stakeholder notification
```

### Guidance

- Keep each task outcome-focused: “Implement X”, “Write QA doc”.
- Use `[P]` suffix for items that can run in parallel safely.
- Attach owners inline when multiple agents share a change (`- [ ] 1.2 [@alex]`).
- Add `[BLOCKED: reason]` to tasks requiring external input, and capture mitigation in `plan.md`.
- Update sub-bullets with file paths, pseudo-steps, and commands as you progress.
- When new scope appears mid-implementation, add a task or spawn a fresh change folder—do not leave it undocumented.
