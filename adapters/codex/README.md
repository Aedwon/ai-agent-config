# Codex Adapter

Codex discovers `AGENTS.md` at project scope and layers files from the project
root toward the current directory. Its global instructions file is
`.codex/AGENTS.md` beneath the user's explicitly supplied home root.

Source reviewed August 25, 2026: [Custom instructions with
AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Project scope renders the full minimal project bundle. Global scope renders only
the universal core. Both write to caller-declared staging; the tool never finds
or changes a home directory. Inspect the diff before manually copying the file.
