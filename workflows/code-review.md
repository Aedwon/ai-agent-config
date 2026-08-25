# Code Review Workflow

## Purpose

Evaluate a fixed change set for defects, regressions, safety gaps, and missing
tests without changing it.

## Inputs

- A fixed review point such as a commit, branch comparison, or supplied diff
- Governing requirements and relevant validation evidence

## Procedure

1. Resolve the exact review boundary and list changed files.
2. Read governing rules and the changed code in its execution context.
3. Trace affected callers, state transitions, trust boundaries, and failure
   paths.
4. Verify plausible findings with source evidence or a focused reproduction.
5. Check tests for observable behavior, meaningful negative cases, and false
   confidence.
6. Rank findings by consequence and state the triggering conditions.
7. Report only actionable findings; separate unresolved questions from defects.

## Stop conditions

Stop when the review boundary moves, required context is missing, or a finding
cannot be distinguished from an intentional design decision.

## Output

Evidence-backed findings ordered by severity, followed by remaining risks and
validation gaps. Review authority does not authorize edits.

## Optional accelerator

An external review skill may deepen language-specific checks when explicitly
selected.
