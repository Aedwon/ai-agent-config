# Level 3: Agent-Heavy

This example adds delegation, review, verification, handoff, decisions, and an
optional skill selection to the normal project layer. Use these controls when
parallel or long-running work makes their cost worthwhile.

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render --root . --adapter codex --output-root "$staging_root"
```
