# Handoff Workflow

## Purpose

Transfer enough verified state for another worker or future task to continue
without reconstructing the project.

## Inputs

- Current objective, working state, decisions, diffs, and validation evidence

## Procedure

1. State what is complete, in progress, blocked, and untouched.
2. Record the exact branch or work area and whether it is clean.
3. List governing decisions and explain any deviation from the plan.
4. Include commands actually run and their results.
5. Identify risks, failed or unproven checks, and concurrent changes to
   preserve.
6. Give one concrete next action with its prerequisites.
7. Link durable project artifacts instead of copying large content.

## Stop conditions

Do not describe guessed state as current. Stop and inspect before handing off
when source, branch, or validation state may have changed.

## Output

A concise continuation record. Creating a handoff grants no authority to
commit, push, publish, deploy, or alter external state.

## Optional accelerator

An external handoff skill may format the record when selected.
