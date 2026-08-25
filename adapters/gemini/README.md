# Gemini CLI Adapter

Gemini CLI uses `GEMINI.md` as its default hierarchical project context file.
Its global context file is `.gemini/GEMINI.md` beneath the user's explicitly
supplied home root. This adapter does not change the configurable filename.

Source updated June 18, 2026 and reviewed August 25, 2026: [Provide context with
GEMINI.md files](https://geminicli.com/docs/cli/gemini-md/).

Project scope renders the full minimal project bundle. Global scope renders only
the universal core. Both write to caller-declared staging; the tool never finds
or changes a home directory. Inspect the diff before manually copying the file.
