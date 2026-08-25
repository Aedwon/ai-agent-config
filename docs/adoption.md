# Adoption

Choose the smallest level that addresses the project's actual coordination
risk. Every level uses the same canonical core and deterministic renderer.

Cloning this repository is inert. It does not change a project, home directory,
or provider configuration.

## Guided setup

For a new project, create an adoption manifest explicitly:

```sh
python3 -m tooling.config init \
  --root /absolute/path/to/ai-agent-config \
  --output /absolute/path/to/project/ai-agent-config.json
```

Interactive init asks for the provider adapter and adoption level. At Levels 2
and 3 it asks for a project type, creates `PROJECT_RULES.md` beside the manifest
when that file does not already exist, and offers to create a personal profile
template at an explicit path you choose.

The initializer never installs provider configuration. Edit the generated
project rules and optional profile before rendering.

For automation, use:

```sh
python3 -m tooling.config init \
  --root /absolute/path/to/ai-agent-config \
  --output /absolute/path/to/project/ai-agent-config.json \
  --adapter codex \
  --level 2 \
  --project-type product-app \
  --non-interactive
```

## Before rendering

Validate the canonical source:

```sh
python3 -m tooling.config validate --root /absolute/path/to/ai-agent-config
```

Render into an explicit staging directory:

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --output-root "$staging_root"
```

Compare against the receiving project without changing it:

```sh
python3 -m tooling.config diff \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project
```

Review the staged result, then copy it manually.

## Level 1: minimal

Use this for a small project or a first trial. The manifest selects one
provider-discovered project entry containing precedence, the universal contract,
and minimal project rules.

No external skills, global manager, specification process, project overlay, or
provider-global change is involved.

You can skip `init` for a manual trial and render directly with
`--adapter codex`.

## Level 2: normal project

Level 2 composes actual selected material into the generated entry:

1. Level 1 universal baseline;
2. `PROJECT_RULES.md` from the project;
3. `software-project` plus a selected project-type delta when applicable;
4. selected neutral workflows.

The default initializer selects planning, implementation, and verification
workflows. Edit the JSON manifest if the project needs a different set.

Use `DECISIONS.md` and `HANDOFF.md` as project-owned artifacts when useful.
External skill packages remain optional.

## Level 3: agent-heavy

Use this when several agents, long-running work, or costly changes justify more
control. The default manifest adds planning, implementation, delegation,
code-review, verification, and handoff workflows plus the software baseline.

Add approved specs, decision records, isolated worktrees, and optional skills
only when they pay for their coordination cost. The main agent still owns
delegated results.

A plan, test pass, handoff, or skill invocation does not grant mutation
authority.

## Level 4: provider-native or global

Level 4 uses global scope. The manifest cannot select project rules, project
types, or project workflows.

Render into staging:

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --output-root "$staging_root"
```

The target root is always supplied by the user during `diff`. Inspect the exact
result, then install through a manual or provider-native mechanism. The tool
does not write the target.

A private profile may be appended explicitly with `--profile`; it is never
discovered automatically.

Run recognition only after reviewing its command and only for an already
available, authenticated provider.

Gemini CLI and Antigravity currently share `.gemini/GEMINI.md` at global scope.
If both are used, maintain one reviewed generated file instead of competing
copies.

## Personal profiles

Profiles are optional and private. They may change tone, formatting, preferred
ceremony, or cost routing. They cannot weaken non-waivable invariants, override
project decisions, or grant mutation authority.

Pass a profile explicitly:

```sh
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --profile /explicit/path/to/profile.md \
  --output-root "$staging_root"
```

See the four executable manifests under `examples/`.
