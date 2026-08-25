# Level 1: Minimal

This manifest renders only the universal baseline plus minimal project rules.

```sh
python3 -m tooling.config render \
  --root . \
  --manifest examples/level-1-minimal/example.json \
  --output-root /tmp/ai-agent-config-level-1
```

No external skills or global configuration are required.
