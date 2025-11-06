# Change & Capability Information Flow

Flow Maestro no longer relies on parent/child issues. Instead, treat each change folder as the parent and each capability delta as the child artifact that must stay aligned.

## Responsibilities

- **Change Folder (`changes/<id>/`)**
  - Owns `spec.md`, `blueprint.md`, `tasks.md`, journals, and QA notes.
  - Aggregates context across capabilities and keeps the timeline updated.
- **Capability Delta (`specs/<capability>/spec.md`)**
  - Describes behavior changes for a single capability.
  - Must stay focused on normative requirements and scenarios.

## Information Flow

1. `/ideate` captures intent in the change folder.
2. `/blueprint` decides which capabilities are touched and seeds delta files.
3. `/work` pushes technical detail into both the journal and the relevant delta files.
4. `/qa` verifies capability outcomes and ensures delta specs are merge-ready.
5. `flowm specs apply` projects the deltas into canonical specs and archives the change.

## Guidelines

- Keep capability deltas short and behavior-focused. If content belongs in the blueprint or journal, do not repeat it in the delta.
- Reference canonical specs by path (`specs/<capability>/spec.md`) when citing behavior in blueprints or QA notes.
- If multiple change folders touch the same capability, coordinate sequencing and run `flowm changes list` to avoid conflicting deltas.
- When a capability needs wholesale rewrite, document the migration strategy in `blueprint.md` and use the delta file to show the final state.
