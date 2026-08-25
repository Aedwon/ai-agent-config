import json
import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT, copy_repository
from tooling.config.render import render
from tooling.config.validate import validate


class MigrationAndExampleTests(unittest.TestCase):
    def assert_error_contains(self, errors, expected):
        self.assertTrue(
            any(expected in error for error in errors),
            "expected {!r} in validation errors:\n{}".format(
                expected, "\n".join(errors)
            ),
        )

    def test_rejects_missing_migration_map(self):
        root = copy_repository(self)
        (root / "docs" / "migration-map.json").unlink()
        errors = validate(root)
        self.assert_error_contains(errors, "docs/migration-map.json")

    def test_rejects_incomplete_migration_map(self):
        root = copy_repository(self)
        path = root / "docs" / "migration-map.json"
        path.write_text(json.dumps({"version": 1, "sources": [{"path": "CLAUDE.base.md", "concepts": [{"name": "collaboration policy", "disposition": "REWRITE", "destination": "core/agent-contract.md", "reason": "portable policy"}]}]}), encoding="utf-8")
        errors = validate(root)
        self.assert_error_contains(errors, "missing legacy source 'SYSTEM_GUIDE.md'")

    def test_rejects_level_one_manifest_with_external_dependency(self):
        root = copy_repository(self)
        example_directory = root / "examples" / "level-1-minimal"
        (example_directory / "example.json").write_text(json.dumps({"version": 1, "level": 1, "scope": "project", "adapter": "codex", "output": "AGENTS.md", "components": ["core/precedence.md", "core/agent-contract.md", "templates/minimal/AGENT_RULES.md"], "project_types": [], "workflows": [], "external_skills": True, "global_configuration": False}), encoding="utf-8")
        errors = validate(root)
        self.assert_error_contains(errors, "Level 1 cannot require external skills")

    def test_level_one_example_renders_declared_output(self):
        manifest_path = REPOSITORY_ROOT / "examples" / "level-1-minimal" / "example.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            rendered = render(REPOSITORY_ROOT, manifest["adapter"], Path(directory) / "staging", manifest_path=manifest_path)
        self.assertEqual(rendered[0].name, manifest["output"])
        self.assertFalse(manifest["external_skills"])
        self.assertFalse(manifest["global_configuration"])

    def test_every_adoption_level_composes_declared_material(self):
        examples = {"level-1-minimal": (1, "project", "AGENTS.md"), "level-2-normal": (2, "project", "AGENTS.md"), "level-3-agent-heavy": (3, "project", "AGENTS.md"), "level-4-provider-global": (4, "global", ".codex/AGENTS.md")}
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory)
            for name, expected in examples.items():
                with self.subTest(example=name):
                    example_root = REPOSITORY_ROOT / "examples" / name
                    manifest_path = example_root / "example.json"
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    level, scope, output = expected
                    self.assertEqual(manifest["level"], level)
                    self.assertEqual(manifest["scope"], scope)
                    self.assertEqual(manifest["output"], output)
                    rendered = render(REPOSITORY_ROOT, manifest["adapter"], staging / name, scope=scope, manifest_path=manifest_path)
                    self.assertEqual(rendered[0].relative_to((staging / name).resolve()).as_posix(), output)
                    body = rendered[0].read_text(encoding="utf-8")
                    for project_type in manifest.get("project_types", []):
                        heading = (REPOSITORY_ROOT / "project-types" / "{}.md".format(project_type)).read_text(encoding="utf-8").splitlines()[0]
                        self.assertIn(heading, body)
                    for workflow in manifest.get("workflows", []):
                        heading = (REPOSITORY_ROOT / "workflows" / "{}.md".format(workflow)).read_text(encoding="utf-8").splitlines()[0]
                        self.assertIn(heading, body)

    def test_level_two_and_three_are_not_level_one_in_disguise(self):
        manifests = [REPOSITORY_ROOT / "examples" / "level-2-normal" / "example.json", REPOSITORY_ROOT / "examples" / "level-3-agent-heavy" / "example.json"]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            level_one = render(REPOSITORY_ROOT, "codex", base / "level-1")[0].read_text(encoding="utf-8")
            for index, manifest_path in enumerate(manifests, start=2):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                body = render(REPOSITORY_ROOT, manifest["adapter"], base / "level-{}".format(index), manifest_path=manifest_path)[0].read_text(encoding="utf-8")
                self.assertNotEqual(body, level_one)


if __name__ == "__main__":
    unittest.main()
