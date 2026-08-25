import os
import stat
import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT


FAKE_RECOGNIZER = r'''
import re
from pathlib import Path

for path in Path.cwd().rglob("*.md"):
    match = re.search(
        r"^AI_AGENT_CONFIG_RECOGNITION:\s*([^\s]+)\s*$",
        path.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match:
        print(match.group(1))
        raise SystemExit(0)
print("UNRECOGNIZED")
'''


class RecognitionRunnerTests(unittest.TestCase):
    def load_api(self):
        try:
            from tests.recognition.run import probe
        except ModuleNotFoundError as error:
            self.fail("recognition runner is missing: {}".format(error))
        return probe

    def make_executable(self, body=FAKE_RECOGNIZER):
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        path = Path(temporary_directory.name) / "provider"
        path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_passes_positive_and_negative_controls_for_command_adapters(self):
        probe = self.load_api()
        executable = self.make_executable()

        for adapter_id in ("codex", "claude", "gemini", "antigravity"):
            with self.subTest(adapter=adapter_id):
                result = probe(REPOSITORY_ROOT, adapter_id, executable=executable)

                self.assertEqual(result.status, "PASS")
                self.assertIn(result.marker_value, result.positive_output)
                self.assertIn("UNRECOGNIZED", result.negative_output)

    def test_manual_adapter_is_unproven(self):
        probe = self.load_api()

        result = probe(REPOSITORY_ROOT, "generic", executable=self.make_executable())

        self.assertEqual(result.status, "UNPROVEN")
        self.assertIn("manual", result.reason)

    def test_missing_executable_is_unproven(self):
        probe = self.load_api()

        result = probe(REPOSITORY_ROOT, "codex", executable=Path("/missing/provider"))

        self.assertEqual(result.status, "UNPROVEN")
        self.assertIn("unavailable", result.reason)

    def test_authentication_failure_is_unproven(self):
        probe = self.load_api()
        executable = self.make_executable(
            'import sys\nprint("authentication required", file=sys.stderr)\nraise SystemExit(3)\n'
        )

        result = probe(REPOSITORY_ROOT, "claude", executable=executable)

        self.assertEqual(result.status, "UNPROVEN")
        self.assertIn("authentication", result.reason)

    def test_ambiguous_output_is_unproven(self):
        probe = self.load_api()
        executable = self.make_executable('print("cannot determine active instructions")\n')

        result = probe(REPOSITORY_ROOT, "codex", executable=executable)

        self.assertEqual(result.status, "UNPROVEN")
        self.assertIn("ambiguous", result.reason)

    def test_available_provider_that_misses_marker_fails(self):
        probe = self.load_api()
        executable = self.make_executable('print("UNRECOGNIZED")\n')

        result = probe(REPOSITORY_ROOT, "codex", executable=executable)

        self.assertEqual(result.status, "FAIL")
        self.assertIn("did not recognize", result.reason)

    def test_probe_stages_no_skills_or_credentials(self):
        probe = self.load_api()
        executable = self.make_executable()
        with tempfile.TemporaryDirectory() as home_directory:
            home = Path(home_directory)
            (home / "credentials.json").write_text("private", encoding="utf-8")
            previous = os.environ.get("HOME")
            os.environ["HOME"] = str(home)
            self.addCleanup(self.restore_home, previous)

            result = probe(REPOSITORY_ROOT, "codex", executable=executable)

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.staged_files, ("AGENTS.md",))
        self.assertFalse(any("SKILL.md" in path for path in result.staged_files))
        self.assertFalse(any("credential" in path.lower() for path in result.staged_files))

    @staticmethod
    def restore_home(previous):
        if previous is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = previous


if __name__ == "__main__":
    unittest.main()
