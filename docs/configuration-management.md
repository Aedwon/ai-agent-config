# Configuration Management

The recommended first-run surface is `setup`, followed by `doctor`. Lower-level
commands remain available for deterministic automation and repository
maintenance.

## Setup

```sh
python3 -m tooling.config setup /absolute/path/to/project
```

`setup` orchestrates validation, initialization, conservative project-type
detection, temporary rendering, optional preview, and explicitly authorized
installation. It does not expose a staging directory during the normal first
run.

The default recommendation is Level 2 / Normal. Existing provider files are not
silently replaced. Interactive replacement requires confirmation;
non-interactive replacement requires both `--yes` and `--replace`.

## Doctor

```sh
python3 -m tooling.config doctor /absolute/path/to/project
```

`doctor` checks source validation, the adoption manifest, project rules, the
selected provider target, and byte-for-byte agreement with the current rendered
configuration. It does not invoke provider executables or prove instruction
recognition.

## Apply

```sh
python3 -m tooling.config apply \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project
```

Interactive apply previews the unified diff before mutation. A missing target
may be created after confirmation. A differing existing target is protected
unless replacement is explicitly authorized. Writes are atomic and constrained
to the adapter-selected path beneath the supplied target root.

## Profile

```sh
python3 -m tooling.config profile \
  --output /explicit/private/path/profile.md
```

Profiles are optional and outside the first-run wizard. The command creates one
new template at an explicit path and refuses overwrite. Profile use remains
explicit through `--profile` on composition commands.

## Validate

```sh
python3 -m tooling.config validate --root /absolute/path/to/ai-agent-config
```

Validation checks required files, core separation, catalog strategy and
provenance, immutable upstream revisions, adaptation licenses, trigger
uniqueness, adapter metadata, safe destination classes, templates, migration
mappings, authorization fixtures, and the Level 1 manifest.

`init`, `render`, `setup`, `apply`, and `doctor` validate the canonical source as
part of their operation where required. A separate validation step is therefore
not needed merely to complete first-run setup. Keep the explicit command for CI,
maintenance, and debugging.

## Init

```sh
python3 -m tooling.config init \
  --root /absolute/path/to/ai-agent-config \
  --output /absolute/path/to/project/ai-agent-config.json
```

`init` is the lower-level configuration-only path. Interactive init asks for a
provider adapter and adoption level; Levels 2 and 3 also select a project type
and create `PROJECT_RULES.md` beside the manifest when needed. Personal profiles
are no longer prompted during the ordinary interactive path.

`init` creates project-owned configuration only. It refuses to write inside the
canonical ai-agent-config source tree and never installs provider-global files.
Use `--non-interactive --adapter ... --level ...` for automation. The retained
`--profile-output` option is explicit compatibility for callers that want to
create a profile at the same time.

## Render

```sh
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --output-root /absolute/path/to/staging
```

A manifest supplies its adapter and scope, so those flags do not need to be
repeated. Without a manifest, pass `--adapter`; scope defaults to `project`.

Use `--profile /explicit/path/to/profile.md` to append a selected private
profile below project workflows. Rendering remains deterministic for the same
canonical sources, manifest-selected project content, and profile bytes.

The output root must exist outside the source tree or be creatable there.
Output is written atomically and constrained below that root. Existing
destination symlinks are rejected.

`render` keeps staging explicit because it is an advanced primitive. `setup`,
`apply`, `diff`, and `doctor` hide temporary staging internally where possible.

## Diff

```sh
python3 -m tooling.config diff \
  --root /absolute/path/to/ai-agent-config \
  --manifest /absolute/path/to/project/ai-agent-config.json \
  --target-root /absolute/path/to/project
```

Diff never changes the target. It exits 0 when bytes match, 1 when it prints a
unified diff, and 2 for invalid input or an operational error. `--profile`
uses the same explicit composition as render.

## Deliberate exclusions

The tooling does not synchronize arbitrary provider state, back up or roll back
unrelated files, copy credentials, discover private home-directory targets, or
manage provider caches and plug-ins. `apply` is intentionally narrow: it may
write only the one adapter-selected generated provider file beneath an explicit
target root.

Provider-native permissions, hooks, settings, and sandboxes remain outside this
repository and should be used for controls that require technical enforcement.
