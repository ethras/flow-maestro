# Change Governance Protocol

This protocol replaces the former parent/child issue rules. It defines how change folders progress and how they interact with canonical specs in `.flow-maestro/projects/<project>/`.

## Core Principles

1. **Single Owner**: Each change folder has a single responsible owner until archived.
2. **Tight Batches**: Keep changes small enough to complete within a few working sessions.
3. **Spec Fidelity**: Delta files describe only the behavior that changes—no copies of the entire spec.

## Change Lifecycle

1. **Start** — `/ideate` reaches ≥95 % confidence; scope documented.
2. **Blueprint** — `/blueprint` produces tasks and delta skeletons.
3. **Execute** — `/work` keeps tasks, journals, and deltas in sync.
4. **Verify** — `/qa` confirms readiness; `flowm specs apply` merges and archives.

## Coordination Rules

- Do not start `/work` until `/blueprint` completes and lists every capability impacted.
- If a change introduces follow-up work, spawn a new change folder rather than overloading the current one.
- Use `flowm changes list` during standups to track active work.
- Archive immediately after specs apply to avoid lingering mutable state.

## Quality Gates

- **Readiness**: `tasks.md` has no unchecked blockers, delta specs validated.
- **Traceability**: Journal references files with `path:line`; QA notes link to commands or logs.
- **Verification**: Automated checks recorded, manual steps reproducible.
- **Documentation**: Canonical specs updated via CLI; README or external docs updated if behavior is externally visible.

## Conflict Handling

- If two changes touch the same capability, sequence them or merge their deltas manually before applying.
- In case of conflicts after `flowm specs apply`, revert the canonical spec in git and re-run `specs apply` after reconciling deltas.
