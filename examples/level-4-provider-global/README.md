# Level 4: Provider-Native or Global

This manifest renders global-scope instructions into staging. It selects no
project rules, project types, or project workflows.

```sh
python3 -m tooling.config render \
  --root . \
  --manifest examples/level-4-provider-global/example.json \
  --output-root /tmp/ai-agent-config-level-4
```

Inspect the exact output before any manual or provider-native installation. The
renderer does not write a home directory or provider configuration directly.
