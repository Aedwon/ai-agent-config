# Planning Workflow

## Purpose

Convert an approved design into reviewable implementation tasks.

## Inputs

- Approved design and active project decisions
- Current repository structure and validation commands

## Procedure

1. Map each requirement to a file or observable result.
2. Define small units with clear inputs, outputs, and dependencies.
3. Order tasks so each leaves a coherent, testable state.
4. For behavior changes, write the failing-test step before implementation.
5. Name exact validation commands and expected outcomes.
6. Identify destructive, Git, publishing, deployment, and external actions
   that require separate authority.
7. Add review and handoff points where failure consequences justify them.

## Stop conditions

Stop if the design lacks a required decision, the plan cannot produce
independently testable states, or implementation would exceed current scope.

## Output

A sequenced plan with file ownership, interfaces, tests, validation, and stop
conditions. A plan does not authorize its mutation steps.

## Optional accelerator

An external planning skill may format or deepen the plan when selected. The
local procedure remains complete without it.
