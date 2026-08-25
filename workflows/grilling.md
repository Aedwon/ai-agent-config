# Grilling Workflow

## Purpose

Stress-test a plan, decision, or idea through an explicit interview.

## Inputs

- The item under review
- Known constraints and decisions

## Procedure

1. Invoke this workflow only when the user explicitly asks for grilling.
2. Inspect discoverable facts instead of asking the user to retrieve them.
3. Map decisions and their dependencies.
4. Ask one decision-owning question at a time.
5. Include a concise recommendation and its meaningful cost.
6. Wait for the answer, update the decision map, and ask the next unblocked
   question.
7. Summarize the shared understanding and request confirmation.

## Stop conditions

Stop when the user ends the interview, a governing conflict appears, or the
next question depends on unavailable evidence.

## Output

A confirmed decision map with assumptions, choices, and unresolved items. The
interview does not authorize implementation.

## Optional accelerator

The local `grilling` skill implements this workflow when explicitly invoked.
