# Adoption

Choose the smallest level that addresses the project's actual coordination
risk. Every level uses the same canonical core and deterministic renderer.

## Before you begin

Use Python 3.9 or newer. Clone this repository, select an adapter, and keep the
source repository separate from the project receiving generated files. All
rendering goes to an explicit staging directory outside the source repository.

Validate the source first:

```sh
python3 -m tooling.config validate --root /absolute/path/to/ai-agent-config
```

## Level 1: minimal

Use this for a small project or a first trial. Render one discovered project
entry containing precedence, the universal contract, and minimal project rules.

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --adapter codex \
  --output-root "$staging_root"
python3 -m tooling.config diff \
  --root /absolute/path/to/ai-agent-config \
  --adapter codex \
  --target-root /absolute/path/to/project
```

Review the result, then copy it manually. No external skills, global manager,
specification process, or provider-global change is involved.

## Level 2: normal project

Start with Level 1, then copy `templates/project/PROJECT_RULES.md` into the
project and fill in only verified commands, boundaries, and conventions. Select
`project-types/software-project.md` plus one meaningful delta overlay when
applicable. Link or copy the neutral workflows the project intends to follow.

Use `DECISIONS.md` for durable choices and `HANDOFF.md` only when continuation
state is useful. External skill packages remain optional.

## Level 3: agent-heavy

Use this when several agents, long-running work, or costly changes justify more
control. Add approved specs and plans, decision records, bounded delegation,
isolated worktrees, verification evidence, and deeper review. Select optional
skills individually only when their trigger owner and provenance are clear.

The main agent still owns delegated results. A plan, test pass, handoff, or
skill invocation does not grant mutation authority.

## Level 4: provider-native or global

Global output contains only the universal core. Render it into staging by
passing `--scope global`:

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --adapter codex \
  --scope global \
  --output-root "$staging_root"
python3 -m tooling.config diff \
  --root /absolute/path/to/ai-agent-config \
  --adapter codex \
  --scope global \
  --target-root /absolute/path/to/home
```

The target root is always supplied by the user. Inspect the exact diff, then
install through a manual or provider-native mechanism. The tool does not write
the target. Run the recognition probe only after reviewing its command and only
for an already available, authenticated provider.

Gemini CLI and Antigravity currently share `.gemini/GEMINI.md` at global scope.
If both are used, maintain one reviewed generated file rather than competing
copies.

See the four executable manifests under `examples/`.
