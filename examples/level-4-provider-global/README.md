# Level 4: Provider-Native or Global

This example renders only the universal core to Codex's documented global path
beneath an explicit staging root. Diff against an explicit home root, inspect
the result, install manually, then run the opt-in recognition probe.

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render \
  --root . --adapter codex --scope global --output-root "$staging_root"
python3 -m tooling.config diff \
  --root . --adapter codex --scope global --target-root /absolute/path/to/home
```

The commands do not install or change global configuration.
