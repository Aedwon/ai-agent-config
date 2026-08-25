# Software Project Baseline

Apply this baseline to projects whose main output includes executable code,
automation, or configuration.

## Boundaries

- Keep modules focused and define stable public interfaces.
- Validate data at trust boundaries and make ownership explicit.
- Follow existing project conventions unless the approved change replaces
  them.

## Change safety

- Establish a clean or understood baseline before implementation.
- Write behavior tests at observable seams before changing behavior.
- Preserve backward compatibility unless the approved scope includes a
  migration.
- Keep secrets, credentials, generated state, and machine-private paths out of
  versioned source.

## Failure behavior

- Handle expected failures explicitly and retain enough context to diagnose
  them.
- Avoid silent fallback when it could hide corruption, lost work, or unsafe
  state.

## Completion

- Run focused tests, the project suite, static validation, and required manual
  checks.
- Report actual evidence, skipped checks, and remaining risk.
