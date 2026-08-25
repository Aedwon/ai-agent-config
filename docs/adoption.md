# Adoption

Choose the smallest adoption level that addresses the project's actual
coordination risk. For most software repositories, start with **Level 2**. Every
level uses the same canonical core and deterministic renderer.

Adoption level and per-task process are separate decisions. The adoption level
controls which reusable rules and workflows are available in a project. For
each individual task, the universal core still requires the least elaborate
process that provides sufficient safety, correctness, and verification.

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
project rules and optional profile before rendering when the project needs
custom rules; the generated defaults are usable without additional setup.

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

The render command prints the exact staged provider file. Compare against the
receiving project without changing it:

```sh
python3 -m tooling.config diff \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project
```

Review the staged result, then copy that generated file to the same relative
location under the project root.

## Per-task process tiers

The selected workflows are available procedures, not a mandatory pipeline. For
each task, choose the highest process tier justified by either complexity or
risk:

- **Trivial or low-risk:** direct execution with the smallest sufficient
  verification.
- **Moderate:** lightweight planning, execution, and focused verification.
- **Complex:** explicit planning, staged implementation, review, and
  verification.
- **High-risk:** explicit authority confirmation, constrained execution, and
  independent verification.

A task can move tiers when new evidence changes its consequence, uncertainty,
reversibility, scope, or risk. Do not add planning, delegation, review, or other
ceremony unless it materially improves safety, correctness, or verifiability.
Independent verification does not require another agent; it can be a test,
external observable, separate inspection path, or reviewer.

## Level 1: minimal

Use this for a tiny project or a first trial. The manifest selects one
provider-discovered project entry containing precedence, the universal contract,
and minimal project rules.

No external skills, global manager, specification process, project overlay, or
provider-global change is involved.

You can skip `init` for a manual trial and render directly with an explicit
`--adapter`.

## Level 2: normal project

Level 2 is the recommended default for most repositories. It composes:

1. Level 1 universal baseline;
2. `PROJECT_RULES.md` from the project;
3. `software-project` plus a selected project-type delta when applicable;
4. selected neutral workflows.

The default initializer includes planning, implementation, and verification as
available workflows. Their presence does not require a plan for every task; the
per-task process tiers above decide how much ceremony is justified.

Use `DECISIONS.md` and `HANDOFF.md` as project-owned artifacts when useful.
External skill packages remain optional.

## Level 3: agent-heavy

Use this when several agents, long-running work, or costly changes justify more
control. The default manifest adds planning, implementation, delegation,
code-review, verification, and handoff workflows plus the software baseline.

These workflows remain conditional tools, not an always-on sequence. A trivial
change in a Level 3 repository can still execute directly when the universal
core classifies it as low-risk.

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
