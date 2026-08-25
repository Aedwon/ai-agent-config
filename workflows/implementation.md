# Implementation Workflow

## Purpose

Execute an approved change while preserving evidence, authority, and nearby
work.

## Inputs

- Approved scope or implementation plan
- Matching authority for each intended mutation class
- A clean or understood baseline

## Procedure

1. Confirm the active branch, work area, governing files, and mutation scope.
2. Inspect concurrent or user-owned changes and preserve them.
3. Run the smallest useful baseline checks.
4. For each behavior, write a test, observe the expected failure, implement the
   smallest passing change, and keep the suite green.
5. For prose and declarative files, validate syntax, references, and observable
   consumer behavior instead of asserting exact wording.
6. Inspect each diff for unrelated changes and private data.
7. Run focused validation before broad validation.
8. Commit only when current authority covers a commit, and keep each commit
   logically reviewable.

## Stop conditions

Stop on contradictory instructions, stale governing state, unexplained
baseline failures, escaping scope, missing authority, or repeated fixes that
produce no new evidence.

## Output

Implemented work, current validation evidence, an honest status, and a clean
handoff. Implementation authority does not imply push, merge, or release
authority.

## Optional accelerator

An external execution or test-first skill may guide these steps when selected.
It remains subordinate to the approved plan and authority.
