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

For most software projects, start with **Level 2**. Use Level 1 for a minimal
trial, Level 3 for unusually agent-heavy work, and Level 4 only for explicit
global/provider-native configuration.

Clone the repository and initialize a manifest for the project you want an agent
to work on:

```sh
git clone https://github.com/Aedwon/ai-agent-config.git
cd ai-agent-config

repo_root="$PWD"
project_root=/absolute/path/to/your-project

python3 -m tooling.config init \
  --root "$repo_root" \
  --output "$project_root/ai-agent-config.json"
```

The initializer asks which provider you use, which adoption level fits the
project, and—at Levels 2 and 3—which project type is closest. It creates only
project-owned configuration files; it does not install provider configuration
or modify a home directory.

Render the selected configuration to a temporary staging directory:

```sh
staging_root=$(mktemp -d)

python3 -m tooling.config render \
  --root "$repo_root" \
  --manifest "$project_root/ai-agent-config.json" \
  --output-root "$staging_root"
```

The command prints the exact staged provider file. Review it, optionally compare
it with the receiving project, then copy that one generated file to the same
relative location under the project root:

```sh
python3 -m tooling.config diff \
  --root "$repo_root" \
  --manifest "$project_root/ai-agent-config.json" \
  --target-root "$project_root"
```

`diff` is read-only and exits with status 1 when it finds a difference. That is
enough to start. External skills, personal profiles, recognition probes, and
global configuration are optional.

For a fully manual Level 1 trial, you can skip the manifest and render directly
with `--adapter codex` (or another supported adapter). See the
[adoption guide](docs/adoption.md) for the longer form.

## Four adoption levels

1. **Minimal:** one project entry with the universal baseline. Best for a first
   trial, tiny repository, or low-coordination work.
2. **Normal project:** compose project rules, a project-type overlay, and useful
   neutral workflows. This is the recommended default for most repositories.
3. **Agent-heavy:** add delegation, deeper review, handoff, and other controls
   when several agents, long-running work, or costly changes justify them.
4. **Provider-native/global:** render the universal core to an explicit staging
   root, inspect the exact diff, install manually, and run an opt-in recognition
   probe when useful.

Adoption level controls which capabilities are available to the agent. It does
**not** prescribe the same amount of ceremony for every task. The universal core
requires the least elaborate per-task process that still provides sufficient
safety, correctness, and verification: trivial work can execute directly,
moderate work gets lightweight planning, complex work gets explicit planning and
review, and high-risk work gets explicit authority and independent verification.

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

A manifest makes Levels 2 and 3 real composition instead of documentation-only
lists. Provider adapters change only discovery mechanics; they do not change
the selected policy body. Selected workflows are available procedures, not a
mandatory pipeline for every task.

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
- `tooling/` validates, initializes, renders, and compares configuration without
  installing it.

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
not discover a home directory, install configuration, copy credentials, or
manage provider caches and plug-ins.

For Antigravity IDE, install the staged project output at
`.agents/rules/ai-agent-config.md`. If the workspace rule is not active
automatically, enable it through the IDE. The separate `agy` CLI cannot prove
IDE rule discovery, so the first recognition check is intentionally manual.

## Personal profiles

Profiles can contain private preferences such as verbosity, spelling, ceremony,
or cost routing. They cannot grant mutation authority or weaken the universal
invariants.

Keep real profiles outside this public repository when they reveal identity,
paths, accounts, or commercial terms. Supply one explicitly with:

```sh
python3 -m tooling.config render \
  --root "$repo_root" \
  --manifest "$project_root/ai-agent-config.json" \
  --profile /explicit/path/to/profile.md \
  --output-root "$staging_root"
```

## Documentation

- [Adoption](docs/adoption.md)
- [Architecture and precedence](docs/architecture.md)
- [Safe configuration management](docs/configuration-management.md)
- [Dependencies and discovery evidence](docs/dependencies.md)
- [Validation and recognition](docs/validation.md)
- [Migration from v1](docs/migration-v1-to-v2.md)

## License and third-party material

Original v2 material is MIT licensed, copyright Aerol Dwayne Balayon.
`THIRD_PARTY_NOTICES.md` identifies the optional upstream packages and local
adaptations. Retained upstream MIT notices live in `LICENSES/`. External
references are pinned to immutable revisions in `skills/catalog.yaml`; the
unchanged skill bodies are not vendored.
