# Dependencies and Discovery Sources

The default tooling uses Python's standard library and requires no installed
skill package, account tier, or specific inference engine. External skill
libraries remain optional references recorded in `skills/catalog.yaml`.

## Immutable external references

| Package | Revision | License | Role |
| --- | --- | --- | --- |
| Matt Pocock skills | `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76` | MIT | Two attributed adaptations and optional references |
| Superpowers | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | MIT | Optional workflow accelerator references |

Both revisions and their license files were verified from the authoritative
repositories on August 25, 2026.

## Provider discovery research

Adapter metadata records project-level discovery only. No adapter installs or
changes global configuration.

- Codex reads `AGENTS.md` from the project root toward the working directory.
  Source reviewed August 25, 2026: [official OpenAI
  documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- Claude Code loads project instructions from `./CLAUDE.md` or
  `./.claude/CLAUDE.md` and layers directory instructions. This project uses
  the root form. Source reviewed August 25, 2026: [Claude Code
  documentation](https://code.claude.com/docs/en/memory).
- Gemini CLI uses hierarchical `GEMINI.md` context by default. Source updated
  June 18, 2026 and reviewed August 25, 2026: [Gemini CLI
  documentation](https://geminicli.com/docs/cli/gemini-md/).
- Antigravity IDE stores workspace rules under `.agents/rules/`. Source
  reviewed August 25, 2026: [Google
  Codelabs](https://codelabs.developers.google.com/getting-started-agy-ide).
- Generic agents have no shared automatic discovery convention. The generic
  adapter therefore produces a manual integration file and makes no automatic
  recognition claim.

These facts describe discovery, not policy precedence. Canonical precedence
remains in `core/precedence.md`.
