You are taking over a Flow Maestro change folder with zero prior context. Your job is to create a crisp handoff note so the next agent (same capabilities) can resume immediately without re-running `/ideate` discovery.

Follow the Strategos loop: reference the active change under `.flow-maestro/projects/<project>/changes/<change-id>/`, cite the exact artifacts you touched (`spec.md`, `plan.md`, `tasks.md`, `notes/journal.md`, `qa.md`, delta specs). If a slash command is mentioned, link it to its Markdown guide in `.flow-maestro/commands/`.

---

## **Objective & Stage**
- **Goal:** [One sentence describing the change outcome tied to the project/change ID]
- **Stage:** [Ideate / Blueprint / Work / QA | % complete | link to file, e.g., `commands/blueprint.md`]
- **Source:** [Linear issue, request doc, or “ad-hoc”]
- **Constraints:** [Deadlines, dependencies, stakeholder mandates, preserving backups, etc.]

## **Critical Context**
- **Key decisions:** [What was chosen, why, and where documented (e.g., `plan.md:45`)]
- **Assumptions:** [Inputs you’re treating as true; note what would break if wrong]
- **Discoveries:** [New info that changed scope or plan; include file/line refs]
- **Resources:** [Docs/scripts/CLI commands consulted, e.g., `flowm research capture`, Context7 lookups]

## **Work Completed**
Bullet each shippable artifact with file path + intent:
- Updated `spec.md` section “Data Model” to add … (reason…)
- Added checklist in `tasks.md` covering … (links to modules…)
- Captured journal entry `notes/journal.md` (timestamp) summarizing …

## **Work Remaining**
Prioritize actionable steps with blockers noted:
- [ ] Finish `tasks.md` item 2.3: implement … (depends on review of …)
- [ ] Update delta spec `specs/payments/spec.md` with scenario … (needs data from API team)
- [ ] Run `/qa` validation checklist once feature flag flipped

## **Verification Done**
List what’s already validated and how:
- `uv run pytest -q` for `services/api` → pass (log in `notes/validation.md`)
- Manual scenario “Upload PDF” in staging env → fails due to …

## **Verification Needed**
What’s left before `flowm specs apply`:
- Must rerun `/qa` checklist after merging PR #123
- Requires approval from stakeholder X on blueprint changes (see Linear link)

## **Blockers & Risks**
- **Blocked on:** [e.g., waiting for schema migration MR]
- **Risks:** [deployment window, delta drift, missing backups]
- **Mitigations:** [backup plan, feature flag, fallback spec update]

## **Next Actions**
1. Most urgent action (include command/file, e.g., “Complete `/work` task 3: refactor `apps/web/...`”)
2. Second priority
3. Third priority

---

Be concrete. Refer to exact files and commands instead of generic prose. If anything is uncertain, flag it explicitly so the next agent knows what to verify before proceeding.
