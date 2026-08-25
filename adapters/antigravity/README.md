# Google Antigravity Adapter

Antigravity IDE stores workspace rules under `.agents/rules/`. This adapter
renders one workspace rule. Its global instructions file is
`.gemini/GEMINI.md` beneath the user's explicitly supplied home root.

Source reviewed August 25, 2026: [Getting Started with Antigravity
IDE](https://codelabs.developers.google.com/getting-started-agy-ide).

Project scope renders the full minimal project bundle. Global scope renders only
the universal core. Both write to caller-declared staging; the tool never finds
or changes a home directory. Inspect the diff before manually copying the file.
Activate the workspace rule through the IDE when required.
