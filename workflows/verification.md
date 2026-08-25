# Verification Workflow

## Purpose

Produce current evidence for every material completion claim.

## Inputs

- Requested outcomes and acceptance criteria
- The final change set and authoritative validation commands

## Procedure

1. Translate each claim into observable evidence.
2. Run fresh focused checks for changed behavior.
3. Run the required broad suite and static validation.
4. Inspect outputs, exit codes, side effects, and warnings.
5. Verify that source and unrelated state remained unchanged.
6. Record unavailable or ambiguous checks as unproven, never as passing.
7. Compare final state with the approved scope and report deviations.

## Stop conditions

Do not claim completion after stale, partial, skipped, or unexplained failing
evidence. Stop when required evidence depends on unavailable authority or an
uncontrolled external system.

## Output

A claim-to-evidence record with actual commands, results, failures, and
unproven items.

## Optional accelerator

An external verification skill may provide a checklist. Fresh evidence remains
the completion gate.
