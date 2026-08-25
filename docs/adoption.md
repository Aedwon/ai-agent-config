# Adoption

Choose the smallest setup mode that addresses the project's actual coordination
risk. For most software repositories, start with **Normal**. Every mode uses the
same canonical core and deterministic renderer.

Setup mode and per-task process are separate decisions. The setup mode controls
which reusable rules and workflows are available in a project. For each
individual task, the universal core still requires the least elaborate process
that provides sufficient safety, correctness, and verification.

Cloning this repository is inert. It does not change a project, home directory,
or provider configuration.

## Guided first run

For a new project, use the guided setup command from the ai-agent-config
repository:

```sh
python3 -m tooling.config setup /absolute/path/to/project
```

The normal path asks for the provider, recommends the Normal setup, and detects
a specialized project type only when strong local signals exist. Otherwise it
uses the `software-project` baseline. It creates the project manifest and
`PROJECT_RULES.md` when applicable, offers an optional diff preview, and asks
before installing the generated provider file.

Existing provider files are not silently replaced. Interactive setup requires a
separate replacement confirmation. Non-interactive `--yes` setup still refuses
to replace a differing existing provider file unless `--replace` is also
supplied.

For scripting, make the provider explicit:

```sh
python3 -m tooling.config setup /absolute/path/to/project \
  --adapter codex \
  --yes
```

`--yes` uses the Normal setup unless `--level` is supplied. Use `--no-apply` to
create only project-owned configuration without installing the generated
provider file.

After setup, check the installation with:

```sh
python3 -m tooling.config doctor /absolute/path/to/project
```

`doctor` validates the source and manifest, checks project-owned rules, and
verifies that the installed provider file still matches the current rendered
configuration. Provider recognition remains a separate opt-in check because it
may invoke an authenticated provider executable.

## Project-type detection

Guided setup is deliberately conservative. It currently recognizes strong
signals for:

- Flutter/mobile product applications;
- common web frameworks such as Next.js, Vite, Astro, and SvelteKit;
- common Discord bot dependencies.

When those signals are absent or ambiguous, setup falls back to
`software-project`. Interactive users can reject a detected type. Advanced and
non-interactive users can pass `--project-type` explicitly.

## Safe apply for existing manifests

To update an existing installation, inspect the diff and apply explicitly:

```sh
python3 -m tooling.config diff \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project

python3 -m tooling.config apply \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project
```

Interactive `apply` prints the diff before mutation. Creating a missing target
requires confirmation. Replacing a differing existing target requires explicit
replacement confirmation. In non-interactive use, `--yes` authorizes the apply,
but replacement still requires `--replace`.

The command writes only the adapter-selected provider file beneath the supplied
target root. It does not write credentials, provider settings, caches, plug-ins,
or home-directory configuration.

## Personal profiles

Personal profiles are optional and intentionally omitted from the first-run
wizard. They may change tone, formatting, preferred ceremony, or cost routing.
They cannot weaken non-waivable invariants, override project decisions, or grant
mutation authority.

Create one later at an explicit private path:

```sh
python3 -m tooling.config profile \
  --output /explicit/path/to/profile.md
```

Pass it explicitly when rendering, diffing, applying, or diagnosing. Profiles
are never discovered automatically.

## Advanced initialization

The lower-level `init` command remains available when you want to create a
manifest without the guided setup or provider-file installation:

```sh
python3 -m tooling.config init \
  --root /absolute/path/to/ai-agent-config \
  --output /absolute/path/to/project/ai-agent-config.json
```

Interactive init asks for the provider adapter and setup level. At Levels 2 and
3 it asks for a project type and creates `PROJECT_RULES.md` beside the manifest
when that file does not already exist. It does not ask about personal profiles
in the normal interactive path; use `profile` separately, or the retained
`--profile-output` option for explicit automation compatibility.

`init` validates the canonical source internally before it creates files, so an
additional `validate` command is not required during ordinary initialization.
Use explicit validation for repository maintenance, CI, or debugging:

```sh
python3 -m tooling.config validate --root /absolute/path/to/ai-agent-config
```

## Advanced rendering

The renderer still supports explicit staging for deterministic inspection and
automation:

```sh
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --output-root /absolute/path/to/staging
```

The guided `setup`, `apply`, `diff`, and `doctor` paths use temporary staging
internally so first-time users do not need to create or manage a staging
directory themselves.

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

## Level 1: Minimal

Use this for a tiny project or a first trial. The manifest selects one
provider-discovered project entry containing precedence, the universal contract,
and minimal project rules.

No external skills, global manager, specification process, project overlay, or
provider-global change is involved.

## Level 2: Normal

Level 2 is the recommended default for most repositories. It composes:

1. Level 1 universal baseline;
2. `PROJECT_RULES.md` from the project;
3. `software-project` plus a selected project-type delta when applicable;
4. selected neutral workflows.

The default includes planning, implementation, and verification as available
workflows. Their presence does not require a plan for every task; the per-task
process tiers above decide how much ceremony is justified.

Use `DECISIONS.md` and `HANDOFF.md` as project-owned artifacts when useful.
External skill packages remain optional.

## Level 3: Agent-heavy

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

## Level 4: Provider-native or global

Level 4 uses global scope. The manifest cannot select project rules, project
types, or project workflows.

Global setup remains an advanced operation. Render into an explicit staging
root, inspect the exact diff, and install through a manual or provider-native
mechanism. The first-run `setup` command is optimized for project scope and does
not silently create home-directory or provider-global state.

A private profile may be appended explicitly with `--profile`; it is never
discovered automatically.

Run recognition only after reviewing its command and only for an already
available, authenticated provider.

Gemini CLI and Antigravity currently share `.gemini/GEMINI.md` at global scope.
If both are used, maintain one reviewed generated file instead of competing
copies.
