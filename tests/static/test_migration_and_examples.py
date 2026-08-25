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
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sources": [
                        {
                            "path": "CLAUDE.base.md",
                            "concepts": [
                                {
                                    "name": "collaboration policy",
                                    "disposition": "REWRITE",
                                    "destination": "core/agent-contract.md",
                                    "reason": "portable policy",
                                }
                            ],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        errors = validate(root)

        self.assert_error_contains(errors, "missing legacy source 'SYSTEM_GUIDE.md'")

    def test_rejects_level_one_manifest_with_external_dependency(self):
        root = copy_repository(self)
        example_directory = root / "examples" / "level-1-minimal"
        example_directory.mkdir(parents=True, exist_ok=True)
        (example_directory / "example.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "level": 1,
                    "adapter": "codex",
                    "output": "AGENTS.md",
                    "components": ["core/agent-contract.md"],
                    "external_skills": True,
                    "global_configuration": False,
                }
            ),
            encoding="utf-8",
        )

        errors = validate(root)

        self.assert_error_contains(errors, "Level 1 cannot require external skills")

    def test_level_one_example_renders_declared_output(self):
        manifest_path = REPOSITORY_ROOT / "examples" / "level-1-minimal" / "example.json"
        if not manifest_path.is_file():
            self.fail("Level 1 example manifest is missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            rendered = render(
                REPOSITORY_ROOT,
                manifest["adapter"],
                Path(directory) / "staging",
            )

        self.assertEqual(rendered[0].name, manifest["output"])
        self.assertFalse(manifest["external_skills"])
        self.assertFalse(manifest["global_configuration"])

    def test_every_adoption_level_has_a_renderable_example(self):
        examples = {
            "level-1-minimal": (1, "project", "AGENTS.md"),
            "level-2-normal": (2, "project", "AGENTS.md"),
            "level-3-agent-heavy": (3, "project", "AGENTS.md"),
            "level-4-provider-global": (4, "global", ".codex/AGENTS.md"),
        }
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory)
            for name, expected in examples.items():
                with self.subTest(example=name):
                    example_root = REPOSITORY_ROOT / "examples" / name
                    self.assertTrue((example_root / "README.md").is_file())
                    manifest = json.loads(
                        (example_root / "example.json").read_text(encoding="utf-8")
                    )
                    level, scope, output = expected
                    self.assertEqual(manifest["level"], level)
                    self.assertEqual(manifest["scope"], scope)
                    self.assertEqual(manifest["output"], output)
                    for field in ("components", "project_files", "workflows"):
                        for relative in manifest.get(field, []):
                            self.assertTrue(
                                (REPOSITORY_ROOT / relative).is_file(),
                                "{} references missing {}".format(name, relative),
                            )
                    rendered = render(
                        REPOSITORY_ROOT,
                        manifest["adapter"],
                        staging / name,
                        scope=scope,
                    )
                    self.assertEqual(
                        rendered[0].relative_to((staging / name).resolve()).as_posix(),
                        output,
                    )


if __name__ == "__main__":
    unittest.main()
