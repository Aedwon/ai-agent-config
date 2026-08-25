# Level 2: Normal Project

This example keeps Level 1 and adds project-owned rules, the shared software
baseline, a product-app delta, and selected neutral workflows. Copy and edit the
project templates in the receiving repository. External skills remain optional.

```sh
staging_root=$(mktemp -d)
python3 -m tooling.config render --root . --adapter codex --output-root "$staging_root"
```
