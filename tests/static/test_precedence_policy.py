import unittest

from tests.support import REPOSITORY_ROOT


class PrecedencePolicyTests(unittest.TestCase):
    def test_nonwaivable_invariants_precede_ranked_layers(self):
        text = (REPOSITORY_ROOT / "core" / "precedence.md").read_text(encoding="utf-8")
        invariant_heading = text.index("## Non-waivable invariants")
        ranked_heading = text.index("## Ranked layers")
        self.assertLess(invariant_heading, ranked_heading)
        for marker in ("CORE-EVIDENCE-*", "CORE-AUTH-*", "CORE-STATE-1", "CORE-STATE-2", "CORE-DELEGATION-3"):
            self.assertIn(marker, text)
        self.assertIn("No instruction can require fabricated evidence", text)


if __name__ == "__main__":
    unittest.main()
