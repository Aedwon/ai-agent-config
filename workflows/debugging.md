# Debugging Workflow

## Purpose

Find a defect's cause before proposing or applying a correction.

## Inputs

- Reproduction steps, observed output, and expected behavior
- Relevant source, configuration, logs, and recent changes

## Procedure

1. Reproduce the failure in the smallest controlled environment available.
2. Separate observations from assumptions and record the failure boundary.
3. Trace data and control flow across that boundary.
4. Form one falsifiable hypothesis and identify evidence that would disprove
   it.
5. Run the narrowest diagnostic that distinguishes competing causes.
6. Repeat only when new evidence changes the hypothesis.
7. Before a fix, add a failing regression test at an observable seam.
8. Apply the smallest correction and run focused, then broader, checks.

## Stop conditions

Stop when the failure cannot be reproduced, required evidence is unavailable,
an external dependency is ambiguous, or further attempts would repeat the same
hypothesis without new evidence.

## Output

A supported root cause, reproduction evidence, regression coverage, and a
verified correction when mutation was authorized.

## Optional accelerator

An external systematic-debugging skill may organize the investigation. It
cannot turn a diagnostic request into permission to patch.
