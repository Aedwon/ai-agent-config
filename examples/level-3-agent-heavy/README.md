# Level 3: Agent-Heavy Project

This example composes the software baseline with planning, implementation,
delegation, code-review, verification, and handoff workflows.

```sh
python3 -m tooling.config render \
  --root . \
  --manifest examples/level-3-agent-heavy/example.json \
  --output-root /tmp/ai-agent-config-level-3
```

Optional skills and worktree isolation are coordination aids, not prerequisites
for the renderer.
