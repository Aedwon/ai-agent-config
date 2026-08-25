import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT, copy_repository


class CommandLineTests(unittest.TestCase):
    def run_command(self, *arguments):
        return subprocess.run([sys.executable, "-m", "tooling.config", *arguments], cwd=str(REPOSITORY_ROOT), check=False, capture_output=True, encoding="utf-8")

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
            completed = self.run_command("render", "--root", str(REPOSITORY_ROOT), "--adapter", "codex", "--output-root", str(output))
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, str((output / "AGENTS.md").resolve()) + "\n")
            self.assertTrue((output / "AGENTS.md").is_file())

    def test_render_command_infers_adapter_and_scope_from_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "staging"
            manifest = REPOSITORY_ROOT / "examples" / "level-2-normal" / "example.json"
            completed = self.run_command("render", "--root", str(REPOSITORY_ROOT), "--manifest", str(manifest), "--output-root", str(output))
            self.assertEqual(completed.returncode, 0)
            body = (output / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# Product Application Overlay", body)
            self.assertIn("# Planning Workflow", body)

    def test_diff_command_uses_diff_exit_status_without_target_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.mkdir()
            completed = self.run_command("diff", "--root", str(REPOSITORY_ROOT), "--adapter", "codex", "--target-root", str(target))
            self.assertEqual(completed.returncode, 1)
            self.assertIn("--- target/AGENTS.md", completed.stdout)
            self.assertEqual(list(target.iterdir()), [])

    def test_noninteractive_init_creates_manifest_and_project_rules_only(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            manifest = project / "ai-agent-config.json"
            completed = self.run_command("init", "--root", str(REPOSITORY_ROOT), "--output", str(manifest), "--adapter", "codex", "--level", "2", "--project-type", "product-app", "--non-interactive")
            self.assertEqual(completed.returncode, 0)
            self.assertTrue(manifest.is_file())
            self.assertTrue((project / "PROJECT_RULES.md").is_file())
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["adapter"], "codex")
            self.assertEqual(data["project_types"], ["software-project", "product-app"])
            self.assertEqual(data["workflows"], ["planning", "implementation", "verification"])
            self.assertEqual(sorted(path.name for path in project.iterdir()), ["PROJECT_RULES.md", "ai-agent-config.json"])

    def test_render_command_supports_explicit_global_staging(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "staging"
            completed = self.run_command("render", "--root", str(REPOSITORY_ROOT), "--adapter", "codex", "--scope", "global", "--output-root", str(output))
            self.assertEqual(completed.returncode, 0)
            self.assertTrue((output / ".codex" / "AGENTS.md").is_file())


if __name__ == "__main__":
    unittest.main()
