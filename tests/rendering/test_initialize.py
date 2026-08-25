import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT
from tooling.config.initialize import initialize
from tooling.config.paths import ConfigError


class InitializeTests(unittest.TestCase):
    def test_refuses_manifest_inside_canonical_source(self):
        with self.assertRaisesRegex(ConfigError, "outside"):
            initialize(REPOSITORY_ROOT, REPOSITORY_ROOT / "ai-agent-config.json", "codex", 1)

    def test_refuses_to_overwrite_existing_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ai-agent-config.json"
            output.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "overwrite"):
                initialize(REPOSITORY_ROOT, output, "codex", 1)

    def test_optional_profile_is_created_only_at_explicit_path(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            output = base / "project" / "ai-agent-config.json"
            profile = base / "private" / "profile.md"
            result = initialize(REPOSITORY_ROOT, output, "codex", 1, profile_output=profile)
            self.assertEqual(result["profile"], profile.resolve())
            self.assertTrue(profile.is_file())
            self.assertEqual(sorted(path for path in base.rglob("*") if path.is_file()), [profile, output])


if __name__ == "__main__":
    unittest.main()
