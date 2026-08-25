# Level 1: Minimal

This example renders Codex project output with only the universal core and the
minimal project template. Validate the repository, render to a temporary
staging root, inspect `AGENTS.md`, and copy it manually. No external skill or
global configuration is required.

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render --root . --adapter codex --output-root "$staging_root"
```
