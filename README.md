# AI Agent Config

AI Agent Config is a portable policy and workflow system for coding agents. It
keeps provider-neutral policy separate from project rules, optional workflows,
personal preferences, and provider discovery.

The repository solves two recurring problems: durable rules tend to become tied
to one provider, and copied instruction files silently drift. It works with
Python's standard library and requires no paid subscription, specific model,
global configuration manager, or external skill library. The referenced Matt
Pocock and Superpowers packages are optional accelerators.

## Quick start: Antigravity IDE

If someone sent you this repository and you use Google Antigravity IDE, this is
the shortest path. Start with **Level 1** for the universal baseline or **Level
2** for a normal software project.

Clone the repository, then initialize a manifest for your project:

```sh
git clone https://github.com/Aedwon/ai-agent-config.git
cd ai-agent-config

repo_root="$PWD"
project_root=/absolute/path/to/your-project

python3 -m tooling.config init \
  --root "$repo_root" \
  --output "$project_root/ai-agent-config.json"
```

When prompted:

- choose `antigravity` as the provider adapter;
- choose Level 1 or Level 2 unless you specifically need the heavier workflows;
- at Level 2, choose the project type that best matches the repository;
- create a personal profile only if you want private preferences such as tone,
  verbosity, or cost routing.

Render the selected configuration to a temporary staging directory:

```sh
staging_root=$(mktemp -d)

python3 -m tooling.config render \
  --root "$repo_root" \
  --manifest "$project_root/ai-agent-config.json" \
  --output-root "$staging_root"
```

Review the generated file at:

```text
$staging_root/.agents/rules/ai-agent-config.md
```

If it looks correct, install it into the project:

```sh
mkdir -p "$project_root/.agents/rules"
cp "$staging_root/.agents/rules/ai-agent-config.md" \
  "$project_root/.agents/rules/ai-agent-config.md"
```

Open the project in Antigravity. If the workspace rule is not active
automatically, enable it through the IDE. Antigravity's documented workspace
rule location is `.agents/rules/`; the first recognition check is intentionally
manual because the separate `agy` CLI cannot prove IDE rule discovery.

That is enough to start using the system. External skill packages and global
configuration are optional.

## Fastest setup

Cloning the repository changes nothing on your machine. To personalize a
project, run the explicit initializer and answer a few small questions:

```sh
repo_root=/absolute/path/to/ai-agent-config
project_root=/absolute/path/to/your-project

python3 -m tooling.config init \
  --root "$repo_root" \
  --output "$project_root/ai-agent-config.json"
```

The initializer asks for the provider adapter and adoption level. At Levels 2
and 3 it also asks for a project type, creates a project-owned
`PROJECT_RULES.md` when one does not already exist, and optionally creates a
personal profile template at a path you choose. It never installs provider
configuration or discovers a home directory.

Then render to staging:

```sh
staging_root=$(mktemp -d)

python3 -m tooling.config validate --root "$repo_root"
python3 -m tooling.config render \
  --root "$repo_root" \
  --manifest "$project_root/ai-agent-config.json" \
  --output-root "$staging_root"
python3 -m tooling.config diff \
  --root "$repo_root" \
  --manifest "$project_root/ai-agent-config.json" \
  --target-root "$project_root"
```

Review the staged provider entry, then copy it into the project yourself.
`diff` is read-only and exits with status 1 when it finds a difference.

For a fully manual Level 1 trial, you can still pass `--adapter codex` without
a manifest. See the [adoption guide](docs/adoption.md).

## Four adoption levels

1. **Minimal:** one project entry with the universal baseline. No external
   skills, global mutation, or planning ceremony.
2. **Normal project:** compose project rules, a project-type overlay, and the
   neutral workflows that fit the work.
3. **Agent-heavy:** add plans, decisions, delegation, isolated worktrees,
   deeper review, and optional skills where the added control is worthwhile.
4. **Provider-native/global:** render the universal core to an explicit staging
   root, inspect the exact diff, install manually, and run an opt-in recognition
   probe.

Adopt only the level that pays for itself. Levels 1 and 2 are fully standalone.

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
the selected policy body.

## Repository layers

- `core/` defines universal invariants, authorization, precedence, evidence,
  delegation, and completion rules.
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
