# Level 2: Normal Project

This example composes the Level 1 baseline with the software baseline, a
product-app overlay, and planning, implementation, and verification workflows.

```sh
python3 -m tooling.config render \
  --root . \
  --manifest examples/level-2-normal/example.json \
  --output-root /tmp/ai-agent-config-level-2
```

A real project created through `init` also references its project-owned
`PROJECT_RULES.md`. External skills remain optional.
