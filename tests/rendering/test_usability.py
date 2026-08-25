import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT
from tooling.config.usability import detect_project_type


class FirstRunUsabilityTests(unittest.TestCase):
    def run_command(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "tooling.config", *arguments],
            cwd=str(REPOSITORY_ROOT),
            check=False,
            capture_output=True,
            encoding="utf-8",
        )

    def test_detect_project_type_recognizes_flutter_product_app(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            (project / "pubspec.yaml").write_text("name: example\n", encoding="utf-8")
            (project / "android").mkdir()
            detected, evidence = detect_project_type(project)
            self.assertEqual(detected, "product-app")
            self.assertIn("pubspec.yaml", evidence)

    def test_detect_project_type_falls_back_conservatively(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            detected, evidence = detect_project_type(project)
            self.assertEqual(detected, "software-project")
            self.assertEqual(evidence, ())

    def test_setup_yes_creates_normal_config_and_applies_provider_file(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            (project / "pubspec.yaml").write_text("name: example\n", encoding="utf-8")
            (project / "android").mkdir()

            completed = self.run_command("setup", str(project), "--adapter", "codex", "--yes")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            manifest = project / "ai-agent-config.json"
            self.assertTrue(manifest.is_file())
            self.assertTrue((project / "PROJECT_RULES.md").is_file())
            self.assertTrue((project / "AGENTS.md").is_file())
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["level"], 2)
            self.assertEqual(data["project_types"], ["software-project", "product-app"])
            body = (project / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# Product Application Overlay", body)
            self.assertIn("Installed AI Agent Config", completed.stdout)

    def test_setup_yes_requires_explicit_provider(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            completed = self.run_command("setup", str(project), "--yes")
            self.assertEqual(completed.returncode, 2)
            self.assertIn("requires --adapter", completed.stderr)
            self.assertEqual(list(project.iterdir()), [])

    def test_apply_refuses_silent_replacement_then_allows_explicit_replace(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            setup = self.run_command("setup", str(project), "--adapter", "codex", "--yes")
            self.assertEqual(setup.returncode, 0, setup.stderr)
            target = project / "AGENTS.md"
            target.write_text("local drift\n", encoding="utf-8")
            manifest = project / "ai-agent-config.json"

            refused = self.run_command(
                "apply",
                "--manifest",
                str(manifest),
                "--target-root",
                str(project),
                "--yes",
            )
            self.assertEqual(refused.returncode, 2)
            self.assertIn("without --replace", refused.stderr)
            self.assertEqual(target.read_text(encoding="utf-8"), "local drift\n")

            replaced = self.run_command(
                "apply",
                "--manifest",
                str(manifest),
                "--target-root",
                str(project),
                "--replace",
                "--yes",
            )
            self.assertEqual(replaced.returncode, 0, replaced.stderr)
            self.assertNotEqual(target.read_text(encoding="utf-8"), "local drift\n")
            self.assertIn("Replaced:", replaced.stdout)

    def test_doctor_reports_current_then_detects_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            setup = self.run_command("setup", str(project), "--adapter", "codex", "--yes")
            self.assertEqual(setup.returncode, 0, setup.stderr)

            healthy = self.run_command("doctor", str(project))
            self.assertEqual(healthy.returncode, 0, healthy.stderr)
            self.assertIn("Configuration is ready.", healthy.stdout)
            self.assertIn("Generated provider file is current", healthy.stdout)

            (project / "AGENTS.md").write_text("drift\n", encoding="utf-8")
            drifted = self.run_command("doctor", str(project))
            self.assertEqual(drifted.returncode, 1)
            self.assertIn("Generated provider file differs", drifted.stdout)
            self.assertIn("Configuration needs attention.", drifted.stdout)

    def test_profile_command_is_explicit_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.md"
            created = self.run_command("profile", "--output", str(profile))
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertTrue(profile.is_file())

            repeated = self.run_command("profile", "--output", str(profile))
            self.assertEqual(repeated.returncode, 2)
            self.assertIn("refusing to overwrite", repeated.stderr)


if __name__ == "__main__":
    unittest.main()
