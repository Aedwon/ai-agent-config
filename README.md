# AI Agent Config

AI Agent Config is a portable policy and workflow system for coding agents. It
keeps provider-neutral policy separate from project rules, optional workflows,
personal preferences, and provider discovery.

The repository solves two recurring problems: durable rules tend to become tied
to one provider, and copied instruction files silently drift. It works with
Python's standard library and requires no paid subscription, specific model,
global configuration manager, or external skill library. The referenced Matt
Pocock and Superpowers packages are optional accelerators.

## Quick start

Clone the repository, then run guided setup against the project you want an
agent to work on:

```sh
git clone https://github.com/Aedwon/ai-agent-config.git
cd ai-agent-config

python3 -m tooling.config setup /absolute/path/to/your-project
```

For most projects, accept the recommended **Normal** setup. The wizard asks for
your provider, conservatively detects a specialized project type when strong
local signals exist, creates project-owned configuration, previews changes on
request, and installs exactly one generated provider file only after explicit
confirmation. Existing provider files are not silently replaced.

The normal first run does not require you to understand manifests, staging
roots, workflow selection, or precedence layers. Those remain available through
the lower-level commands for automation and advanced use.

After setup, verify the installation at any time with:

```sh
python3 -m tooling.config doctor /absolute/path/to/your-project
```

`doctor` checks the canonical source, manifest, project rules, provider target,
and whether the installed generated file still matches the current rendered
configuration.

Personal preferences are intentionally outside the first-run wizard. Create an
optional private profile later with:

```sh
python3 -m tooling.config profile \
  --output /explicit/private/path/profile.md
```

## Version and self-verification

The scaffold version is recorded in the repository-root `VERSION` file. A clone
can identify the policy and tooling generation it started from with:

```sh
cat VERSION
```

Before sharing changes or updating a clone, run the same self-verification entry
point used by CI:

```sh
python3 -m tooling.verify
```

It checks the version marker and relevant whitespace, runs the unit-test suite,
and validates the canonical repository. The hosted `Verify` workflow runs the
same command for pull requests, updates to `main`, and manual dispatches so local
and hosted checks stay aligned. See [Versioning](docs/versioning.md) for the
SemVer policy.

## Setup modes

1. **Minimal:** one project entry with the universal baseline. Best for a first
   trial, tiny repository, or low-coordination work.
2. **Normal:** compose project rules, a project-type overlay, and useful neutral
   workflows. This is the recommended default for most repositories.
3. **Agent-heavy:** add delegation, deeper review, handoff, and other controls
   when several agents, long-running work, or costly changes justify them.
4. **Provider-native/global:** render the universal core to an explicit staging
   root, inspect the exact diff, install manually, and run an opt-in recognition
   probe when useful.

Setup mode controls which capabilities are available to the agent. It does
**not** prescribe the same amount of ceremony for every task. The universal core
requires the least elaborate per-task process that still provides sufficient
safety, correctness, and verification: trivial work can execute directly,
moderate work gets lightweight planning, complex work gets explicit planning and
review, and high-risk work gets explicit authority and independent verification.

The underlying manifest still records levels `1` through `4` for compatibility
and deterministic composition. The guided UX calls them setup modes so a new
user does not need to learn the internal terminology first.

## Safe installation and updates

Guided `setup` is the recommended path for a new project. For an existing
manifest, compare and apply explicitly:

```sh
python3 -m tooling.config diff \
  --root "$PWD" \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project

python3 -m tooling.config apply \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project
```

`diff` is read-only. `apply` shows the generated change before mutation in
interactive use. It creates a missing provider file after confirmation but will
not replace a differing existing file unless replacement is explicitly
confirmed or `--replace` is supplied. For non-interactive automation, `--yes`
is explicit authorization; replacing an existing file still requires
`--replace`.

The lower-level `init`, `render`, `diff`, and `validate` commands remain
available when you need deterministic staging, CI validation, or scripted
composition. See the [adoption guide](docs/adoption.md) for details.

## How composition works

The renderer uses one explicit composition order:

1. non-waivable invariants and ranked precedence;
2. universal agent contract;
3. minimal project rules for project scope;
4. project-owned rules selected by the manifest;
5. selected project-type overlays;
6. selected workflows;
7. an explicitly supplied private profile.

The first layer contains truthfulness, evidence, scope-bound mutation
authority, state protection, and main-agent verification. Those invariants are
not waivable by a lower layer or by ordinary workflow preferences.

A manifest makes Normal and Agent-heavy setup real composition instead of
documentation-only lists. Provider adapters change only discovery mechanics;
they do not change the selected policy body. Selected workflows are available
procedures, not a mandatory pipeline for every task.

## Repository layers

- `core/` defines universal invariants, authorization, precedence, evidence,
  delegation, completion rules, and per-task process proportionality.
- `templates/` holds minimal and project-owned starter files.
- `project-types/` adds reusable domain deltas. Start with the software
  baseline, then add a relevant overlay.
- `workflows/` documents portable ways to design, plan, implement, debug,
  review, delegate, verify, and hand off work.
- `profiles/` shows how to keep personal style preferences private and below
  project rules.
- `adapters/` records discovery paths and renders thin provider entry files.
- `skills/` catalogs optional external references and two attributed local
  adaptations. Core operation does not load them.
- `tooling/` validates, initializes, renders, compares, applies, diagnoses, and
  guides first-run configuration without installing credentials or provider
  software.

## Supported adapters

| Adapter | Project output | Global output beneath an explicit root |
| --- | --- | --- |
| Generic | `AGENT_RULES.md` | `AGENT_RULES.md` |
| Codex | `AGENTS.md` | `.codex/AGENTS.md` |
| Claude Code | `CLAUDE.md` | `.claude/CLAUDE.md` |
| Gemini CLI | `GEMINI.md` | `.gemini/GEMINI.md` |
| Google Antigravity IDE | `.agents/rules/ai-agent-config.md` | `.gemini/GEMINI.md` |

Adapters describe behavioral instruction discovery, not a hard security
boundary. Provider-native hooks, permissions, settings, or sandboxing remain
the place for controls that must be technically enforced.

The renderer always requires an explicit source root and staging root. It does
not discover a home directory, copy credentials, or manage provider caches and
plug-ins. Guided setup and `apply` may write only the selected generated
provider file beneath an explicit project target, subject to overwrite guards.

For Antigravity IDE, install the generated project output at
`.agents/rules/ai-agent-config.md`. If the workspace rule is not active
automatically, enable it through the IDE. The separate `agy` CLI cannot prove
IDE rule discovery, so the first recognition check is intentionally manual.

## Project-type detection

Guided setup only selects a specialized project type when it finds strong,
local evidence. Current detection recognizes common Flutter/mobile product-app
signals, common web-framework configuration or dependencies, and common Discord
bot dependencies. When confidence is weak it falls back to the generic
`software-project` baseline instead of guessing.

The detected type is only a setup default. Interactive users can reject it, and
advanced/non-interactive users can pass an explicit `--project-type`.

## Personal profiles

Profiles can contain private preferences such as verbosity, spelling, ceremony,
or cost routing. They cannot grant mutation authority or weaken the universal
invariants.

Keep real profiles outside this public repository when they reveal identity,
paths, accounts, or commercial terms. Create a template explicitly with
`profile`, then pass it when rendering, diffing, applying, or diagnosing:

```sh
python3 -m tooling.config profile \
  --output /explicit/path/to/profile.md

python3 -m tooling.config apply \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --profile /explicit/path/to/profile.md \
  --target-root /absolute/path/to/project
```

## Advanced commands

The original deterministic primitives remain stable building blocks:

```sh
python3 -m tooling.config init \
  --root /absolute/path/to/ai-agent-config \
  --output /absolute/path/to/project/ai-agent-config.json

python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --output-root /absolute/path/to/staging

python3 -m tooling.config validate \
  --root /absolute/path/to/ai-agent-config
```

`init` validates the canonical source before it writes project-owned setup
files, so a separate `validate` invocation is not required during ordinary
first-run setup. `validate` remains useful for CI, repository maintenance, and
explicit integrity checks.

## Documentation

- [Adoption](docs/adoption.md)
- [Architecture and precedence](docs/architecture.md)
- [Safe configuration management](docs/configuration-management.md)
- [Dependencies and discovery evidence](docs/dependencies.md)
- [Validation and recognition](docs/validation.md)
- [Versioning](docs/versioning.md)
- [Migration from v1](docs/migration-v1-to-v2.md)

## License and third-party material

Original v2 material is MIT licensed, copyright Aerol Dwayne Balayon.
`THIRD_PARTY_NOTICES.md` identifies the optional upstream packages and local
adaptations. Retained upstream MIT notices live in `LICENSES/`. External
references are pinned to immutable revisions in `skills/catalog.yaml`; the
unchanged skill bodies are not vendored.
