# Origin of `testing-at-seams`

This local skill is an adaptation and synthesis of Matt Pocock's test-design
guidance.

- Upstream repository: <https://github.com/mattpocock/skills>
- Primary source path: `skills/engineering/tdd/tests.md`
- Related skill path: `skills/engineering/tdd/SKILL.md`
- Comparison revision: `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`
- License: MIT
- Retained copyright: Copyright (c) 2026 Matt Pocock
- Retained notice: `LICENSES/matt-pocock-skills-MIT.txt`

## Local changes

- Extracts observable-seam selection into a small explicit planning aid.
- Adds boundary guidance for external systems and legacy characterization.
- Keeps behavior-owning components real and avoids private implementation tests.
- Declines automatic test ownership and returns control to the normal test-first
  workflow.
- Prohibits implementation while the skill is selecting test architecture.

This file records adaptation lineage; it does not claim ownership of the
upstream material.
