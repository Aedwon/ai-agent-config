# Utility Script Overlay

Baseline: `software-project.md`

Use lighter ceremony for a focused tool while retaining these safeguards.

- Keep setup and dependencies minimal; prefer the language's standard library
  when it remains clear and reliable.
- Validate inputs before mutation, use explicit source and destination paths,
  and reject traversal or ambiguous targets.
- Make output formats deterministic and document exit status and error output.
- Default to preview or read-only behavior for consequential file changes.
- Test important parsing, transformation, boundary, and failure logic through
  the public command or function interface.
- Provide one direct validation command and a short usage example.
