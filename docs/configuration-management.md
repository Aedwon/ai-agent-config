# Configuration Management

The default tool exposes three operations: `validate`, `render`, and `diff`.
All require explicit roots. None discovers a home directory or installs files.

## Validate

```sh
python3 -m tooling.config validate --root /absolute/path/to/ai-agent-config
```

Validation checks required files, core separation, catalog strategy and
provenance, immutable upstream revisions, adaptation licenses, trigger
uniqueness, adapter metadata, safe destination classes, templates, migration
mappings, authorization fixtures, and the Level 1 manifest.

## Render

```sh
python3 -m tooling.config render \
  --root /absolute/path/to/ai-agent-config \
  --adapter claude \
  --scope project \
  --output-root /absolute/path/to/staging
```

`scope` defaults to `project`; `global` is also accepted. The output root must
exist outside the source tree or be creatable there. Output is deterministic,
written atomically, and constrained below that root. Existing destination
symlinks are rejected.

## Diff

```sh
python3 -m tooling.config diff \
  --root /absolute/path/to/ai-agent-config \
  --adapter claude \
  --scope project \
  --target-root /absolute/path/to/project
```

Diff never changes the target. It exits 0 when bytes match, 1 when it prints a
unified diff, and 2 for invalid input or an operational error.

## Deliberate exclusions

The default layer does not apply, synchronize, back up, roll back, or remove
configuration. It does not copy credentials, adoption tokens, caches, plug-ins,
or machine-private data. Advanced apply, sync, and rollback could be designed
later as a separate, explicitly authorized system with recovery guarantees.
They are not implied by the current renderer.
