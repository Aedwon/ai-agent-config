# Migrating from v1 to v2

V2 preserves useful concepts from the original public files while replacing a
provider-named file stack with canonical policy, optional workflows, overlays,
and generated adapters. The machine-readable mapping is `migration-map.json`.

## Source disposition

| V1 source | Disposition | V2 location | Reason |
| --- | --- | --- | --- |
| `CLAUDE.base.md` | REWRITE | `core/agent-contract.md` | Evidence, pushback, and mutation safety survive without the personal persona or runtime defaults. |
| `CLAUDE.base.md` | DROP | private profile or overlay | Personal teaching and product preferences are not universal policy. |
| `CLAUDE.session.md` | KEEP | `workflows/handoff.md` | Verified continuation state remains useful. |
| `CLAUDE.session.md` | DROP | none | A private mode-prefix grammar no longer outranks explicit instructions. |
| `CLAUDE.stack.template.md` | REWRITE | `project-types/` and project rules | Small reusable deltas replace a monolithic stack template. |
| `PATTERNS.template.md` | KEEP | `templates/project/PROJECT_RULES.md` | Stable project patterns still belong near project source. |
| `NEW_PROJECT_SETUP.md` | REWRITE | `docs/adoption.md` | Four proportional levels replace one personal checklist. |
| `NEW_PROJECT_SETUP.md` | REFERENCE | this guide | Historical provider pointers explain the transition but are no longer canonical. |
| `SYSTEM_GUIDE.md` | REWRITE | `docs/architecture.md` | The new guide separates source, selected layers, adapters, and generated state. |
| `SYSTEM_GUIDE.md` | DROP | none | Routine automatic commits violated matching mutation authorization. |

KEEP means the concept remains materially intact. REWRITE keeps the goal while
changing its public form. REFERENCE retains historical context without making
it canonical. DROP records a deliberate retirement rather than erasing history.

## Why two behaviors were retired

Mode prefixes were convenient private aliases, but making them a precedence
layer allowed shorthand to conflict with explicit current instructions and
approved project state. V2 uses explicit workflow selection below project rules.
A private profile may still define aliases, but they cannot weaken higher
authority.

Routine automatic commits were removed because completion, a test pass, or a
workflow does not authorize Git mutation. A commit now requires matching user
authority.

## Why provider files are generated

V1 recommended three duplicated provider pointers. Their content and discovery
claims could drift, and the filenames became the visible architecture. V2 keeps
one canonical core and records discovery in adapters. Rendering produces the
correct project or global filename without forking policy semantics.

The six v1 files remain available in Git history and the preserved archives.
They are removed from the v2 working tree only after every public concept has a
recorded disposition.
