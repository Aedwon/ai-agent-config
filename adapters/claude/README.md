# Claude Code Adapter

Claude Code loads `CLAUDE.md` at project scope and can layer instructions along
the directory hierarchy. Its global instructions file is
`.claude/CLAUDE.md` beneath the user's explicitly supplied home root.

Source reviewed August 25, 2026: [How Claude remembers your
project](https://code.claude.com/docs/en/memory).

Project scope renders the full minimal project bundle. Global scope renders only
the universal core. Both write to caller-declared staging; the tool never finds
or changes a home directory. Inspect the diff before manually copying the file.
