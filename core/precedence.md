---
policy_version: 2
scope: universal
kind: precedence
---

# Precedence

Apply instructions in this order:

1. Explicit current user instruction and matching mutation authorization
2. Active approved project specifications, plans, and decisions
3. Project-local rules
4. Explicitly selected workflows
5. Personal profile
6. Shared universal core
7. Runtime adapter heuristics

A lower layer may add detail only within the freedom left by higher layers. It
cannot weaken, reinterpret, or silently bypass a higher rule.

## Resolution procedure

1. Gather the instructions that govern the current action.
2. Reject stale or inactive project artifacts.
3. Identify conflicts before mutating state.
4. Apply the highest active instruction that covers the question.
5. Combine lower instructions only when they remain compatible.
6. Stop and request the smallest necessary decision when equal-rank
   instructions conflict or the active state cannot be established.

Authority stays attached to its originating instruction. A lower layer cannot
infer a mutation grant from a goal, a workflow step, or prior unrelated
approval.
