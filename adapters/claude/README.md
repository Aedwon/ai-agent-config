# Claude Code Adapter

Claude Code loads `CLAUDE.md` at project scope and can layer instructions along
the directory hierarchy. This adapter renders the root project entry only; it
does not write user, local, or managed configuration.

Source reviewed August 25, 2026: [How Claude remembers your
project](https://code.claude.com/docs/en/memory).

Render into staging and inspect the diff before copying the file into a project.
The template changes no canonical policy semantics.
