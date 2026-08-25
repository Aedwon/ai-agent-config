# Architecture

The repository separates policy, project composition, and provider discovery.
Provider entry files are generated projections, never the canonical source.

## Invariants and precedence

Before the ranked layers, the system applies non-waivable invariants from the
universal contract:

- evidence and completion claims stay truthful;
- mutation authority stays attached to the action, target, environment, and
  scope that granted it;
- workflows and lower layers cannot manufacture additional authority;
- unrelated user and concurrent state is preserved;
- unresolved governing conflicts or stale required state stop mutation;
- the main agent verifies delegated results before relying on them.

After those invariants, the effective order is:

1. explicit current user instruction and matching mutation authorization;
2. active approved project specifications, plans, and decisions;
3. project-local rules;
4. explicitly selected workflows;
5. personal profile;
6. shared universal defaults not classified as invariants;
7. runtime adapter heuristics.

A user can explicitly change scope, grant authority, or resolve a conflict.
That changes the governing state; it does not permit fabricated evidence or
silent authority escalation.

## Canonical and generated state

`core/` is the universal contract. It contains no provider name, personal
preference, subscription choice, or provider filename. `templates/minimal/`
adds the project entry used at Level 1.

Levels 2 and 3 use an explicit JSON adoption manifest. The renderer composes:

1. the universal core;
2. minimal project rules for project scope;
3. a project-owned rules file referenced relative to the manifest;
4. named `project-types/` overlays;
5. named `workflows/`;
6. an optional profile supplied by an explicit path.

The manifest stores portable project selections. A private profile path is
passed at render time instead of being silently discovered or committed.

`profiles/` is deliberately below project rules. A profile can express tone,
formatting, ceremony, or routing preferences without changing public defaults
or granting authority.

Each adapter contains constrained JSON metadata and an identical one-slot
template. The renderer validates the repository, composes the selected bundle,
substitutes it once, and writes an atomic file beneath a declared staging root.
Global scope contains the universal core plus an explicitly supplied profile,
if any. Project-only material is rejected from a global manifest.

## Skills and trigger ownership

Portable workflow documentation works with zero installed skills. The skill
catalog records either an attributed local adaptation or an immutable external
reference, never both for one entry. Locally maintained grilling and seam-test
skills are explicit-only. Optional package-managed accelerators may recommend
an automatic trigger owner, but overlapping automatic owners are rejected.

## Trust boundaries

The validator constrains paths, destinations, provenance, retained licenses,
placeholders, trigger ownership, adapter metadata, migration mappings, and
example manifests. The renderer rejects output below the source tree and
rejects symlink escapes. Project rules referenced by a manifest must stay below
the manifest's directory. Profiles require an explicit file path. The diff
command reads only a user-supplied target and renders comparison bytes in a
temporary directory.

Unknown private paths, credentials, account data, provider caches, and plug-ins
are outside the managed surface. Installed files are generated state and can be
reconstructed from reviewed canonical sources.

Provider instruction files are behavioral context, not hard security
enforcement. Use provider-native permissions, hooks, settings, or sandboxing
when a control must be technically enforced.
