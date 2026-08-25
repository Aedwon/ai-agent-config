---
name: testing-at-seams
description: Choose observable test seams and integration boundaries when the user explicitly asks to plan test coverage or test architecture.
---

# Testing at Seams

Invoke this skill only for an explicit test-architecture request. It complements
a normal test-first cycle and does not own automatic test triggers.

1. Name the user-visible behavior and the smallest seam that can observe it.
   Prefer a public interface and stable result over private methods, internal
   calls, or source structure.
2. At an integration seam, keep the components that own the behavior real.
   Cross a boundary only when that boundary belongs to the contract.
3. At an external-system boundary, use a controlled fake or sandbox that
   mirrors the required contract. Keep routine tests independent of live
   systems.
4. For legacy code, first add a characterization test at its public boundary.
5. State the seam, protected behavior, and required fixture or fake. Return to
   the normal test-first cycle after selecting the seam.

Do not implement the feature while using this planning skill.
