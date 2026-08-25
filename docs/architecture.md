# Architecture

The repository separates policy from discovery. Provider entry files are
generated projections, never the canonical source.

## Layers and precedence

The effective order is:

1. explicit current user instruction and matching mutation authorization;
2. active approved project specifications, plans, and decisions;
3. project-local rules;
4. explicitly selected workflows;
5. personal profile;
6. shared universal core;
7. provider adapter heuristics.

A lower layer cannot weaken a higher layer. In particular, a skill, workflow,
or provider default cannot authorize a Git, destructive, publishing,
deployment, or external mutation.

## Canonical and generated state

`core/` is the universal contract. It contains no provider name, personal
preference, subscription choice, or provider filename. `templates/minimal/`
adds the project entry used at Level 1. `templates/project/`, `project-types/`,
and `workflows/` are selected project-owned material rather than an automatic
global bundle.

`profiles/` is deliberately below project rules. A profile can express a
person's tone, formatting, or preferred level of ceremony without changing the
public defaults.

Each adapter contains constrained JSON metadata and an identical one-slot
template. The renderer validates the repository, selects the canonical bundle,
substitutes it once, and writes an atomic file beneath a declared staging root.
Project scope includes the minimal project template. Global scope includes only
the universal core.

## Skills and trigger ownership

Portable workflow documentation works with zero installed skills. The skill
catalog records either an attributed local adaptation or an immutable external
reference, never both for one entry. Locally maintained grilling and seam-test
skills are explicit-only. Optional package-managed accelerators may recommend
an automatic trigger owner, but overlapping automatic owners are rejected.

## Trust boundaries

The validator constrains paths, destinations, provenance, retained licenses,
placeholders, and trigger ownership. The renderer rejects output below the
source tree and rejects symlink escapes. The diff command reads only a
user-supplied target and renders comparison bytes in a temporary directory.

Unknown private paths, credentials, account data, provider caches, and plug-ins
are outside the managed surface. Installed files are generated state and can
always be reconstructed from reviewed canonical sources.
