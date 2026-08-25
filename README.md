# AI Agent Config

AI Agent Config is a portable policy and workflow system for coding agents. It
keeps one provider-neutral source of truth, then renders the entry filename that
each supported agent discovers.

The repository solves two recurring problems: durable rules tend to become tied
to one provider, and copied instruction files silently drift. Here, universal
policy, project rules, workflows, personal preferences, and provider discovery
stay separate.

It works with Python's standard library. It requires no paid subscription,
specific model, global configuration manager, or external skill library. The
referenced Matt Pocock and Superpowers packages are optional accelerators.

## Fastest setup: Level 1

Level 1 produces one provider-discovered project file containing the universal
baseline and minimal project rules.

```sh
repo_root=/absolute/path/to/ai-agent-config
project_root=/absolute/path/to/your-project
staging_root=$(mktemp -d)

python3 -m tooling.config validate --root "$repo_root"
python3 -m tooling.config render \
  --root "$repo_root" \
  --adapter codex \
  --output-root "$staging_root"
python3 -m tooling.config diff \
  --root "$repo_root" \
  --adapter codex \
  --target-root "$project_root"
```

Review the staged `AGENTS.md`, then copy it into the project yourself. Replace
`codex` with `claude`, `gemini`, `antigravity`, or `generic`. `diff` is
read-only and exits with status 1 when it finds a difference.

See the complete [Level 1 example](examples/level-1-minimal/README.md) and
[adoption guide](docs/adoption.md).

## Four adoption levels

1. **Minimal:** one project entry with the universal baseline. No external
   skills, global mutation, or planning ceremony.
2. **Normal project:** add project rules, a project-type overlay, and the local
   workflows that fit the work.
3. **Agent-heavy:** add plans, decisions, delegation, isolated worktrees,
   deeper review, and optional skills where the added control is worthwhile.
4. **Provider-native/global:** render the universal core to an explicit staging
   root, inspect the exact diff, install manually, and run an opt-in recognition
   probe. Installed state remains generated state.

Adopt only the level that pays for itself. Levels 1 and 2 are fully standalone.

## How the layers fit

- `core/` defines universal authorization, precedence, evidence, delegation,
  and completion rules.
- `templates/` holds minimal and project-owned files.
- `project-types/` adds only reusable domain deltas. Start with the software
  baseline, then select a relevant overlay.
- `workflows/` documents portable ways to design, plan, implement, debug,
  review, delegate, verify, and hand off work.
- `profiles/` shows how to keep personal style preferences private and below
  project rules.
- `adapters/` records discovery paths and renders thin provider entry files.
- `skills/` catalogs optional external references and two attributed local
  adaptations. Core operation does not load them.

Put repository-specific commands, boundaries, and conventions in a copy of
`templates/project/PROJECT_RULES.md`. Put stable product-type concerns in a
selected `project-types/` overlay. Put personal tone, formatting, and routing
preferences in a private profile, not the universal core.

## Supported adapters

| Adapter | Project output | Global output beneath an explicit root |
| --- | --- | --- |
| Generic | `AGENT_RULES.md` | `AGENT_RULES.md` |
| Codex | `AGENTS.md` | `.codex/AGENTS.md` |
| Claude Code | `CLAUDE.md` | `.claude/CLAUDE.md` |
| Gemini CLI | `GEMINI.md` | `.gemini/GEMINI.md` |
| Google Antigravity IDE | `.agents/rules/ai-agent-config.md` | `.gemini/GEMINI.md` |

Adapters change discovery mechanics, not policy semantics. The renderer always
requires an explicit source root and staging root. It does not discover a home
directory, install configuration, copy credentials, or manage provider caches
and plug-ins.

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
