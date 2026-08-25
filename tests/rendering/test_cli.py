import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT, copy_repository


class CommandLineTests(unittest.TestCase):
    def run_command(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "tooling.config", *arguments],
            cwd=str(REPOSITORY_ROOT),
            check=False,
            capture_output=True,
            encoding="utf-8",
        )

    def test_validate_command_accepts_repository(self):
        completed = self.run_command("validate", "--root", str(REPOSITORY_ROOT))

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "OK\n")
        self.assertEqual(completed.stderr, "")

    def test_validate_command_reports_invalid_repository(self):
        root = copy_repository(self)
        core = root / "core" / "agent-contract.md"
        core.write_text(core.read_text(encoding="utf-8") + "\nCodex\n", encoding="utf-8")

        completed = self.run_command("validate", "--root", str(root))

        self.assertEqual(completed.returncode, 1)
        self.assertIn("forbidden universal term 'Codex'", completed.stderr)

    def test_render_command_writes_only_to_explicit_output_root(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "staging"

            completed = self.run_command(
                "render",
                "--root",
                str(REPOSITORY_ROOT),
                "--adapter",
                "codex",
                "--output-root",
                str(output),
            )

            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, str((output / "AGENTS.md").resolve()) + "\n")
            self.assertTrue((output / "AGENTS.md").is_file())

    def test_diff_command_uses_diff_exit_status_without_target_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.mkdir()

            completed = self.run_command(
                "diff",
                "--root",
                str(REPOSITORY_ROOT),
                "--adapter",
                "codex",
                "--target-root",
                str(target),
            )

            self.assertEqual(completed.returncode, 1)
            self.assertIn("--- target/AGENTS.md", completed.stdout)
            self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
