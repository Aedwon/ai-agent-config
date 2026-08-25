# Configuration Management

The default tool exposes four operations: `validate`, `init`, `render`, and
`diff`. None installs provider configuration or discovers a home directory.

## Validate

```sh
python3 -m tooling.config validate --root /absolute/path/to/ai-agent-config
```

Validation checks required files, core separation, catalog strategy and
provenance, immutable upstream revisions, adaptation licenses, trigger
uniqueness, adapter metadata, safe destination classes, templates, migration
mappings, authorization fixtures, and the Level 1 manifest.

## Init

```sh
python3 -m tooling.config init \
  --root /absolute/path/to/ai-agent-config \
  --output /absolute/path/to/project/ai-agent-config.json
```

Interactive init asks for a provider adapter and adoption level. Levels 2 and 3
also select a project type, create `PROJECT_RULES.md` beside the manifest when
it does not already exist, and may create a personal profile template only at
an explicit path supplied by the user.

`init` creates project-owned configuration only. It refuses to write inside the
canonical ai-agent-config source tree and never installs provider-global files.
Use `--non-interactive --adapter ... --level ...` for automation.

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

The default layer does not apply, synchronize, back up, roll back, or remove
provider configuration. It does not copy credentials, adoption tokens, caches,
plug-ins, or machine-private data. Advanced apply, sync, and rollback could be
designed later as a separate, explicitly authorized system with recovery
guarantees. They are not implied by the current renderer.
