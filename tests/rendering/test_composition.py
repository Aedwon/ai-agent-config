import json
import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT
from tooling.config.composition import load_manifest
from tooling.config.paths import ConfigError
from tooling.config.render import render


class CompositionTests(unittest.TestCase):
    def write_manifest(self, base: Path, data):
        path = base / "ai-agent-config.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def base_manifest(self, level=2, scope="project"):
        return {
            "version": 1,
            "level": level,
            "scope": scope,
            "adapter": "codex",
            "output": "AGENTS.md" if scope == "project" else ".codex/AGENTS.md",
            "project_types": [],
            "workflows": [],
            "external_skills": "optional",
            "global_configuration": scope == "global",
        }

    def test_rejects_project_rules_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = self.base_manifest()
            data["project_rules"] = "../outside.md"
            manifest = self.write_manifest(base, data)
            with self.assertRaisesRegex(ConfigError, "stay below"):
                load_manifest(manifest)

    def test_rejects_level_one_workflow_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = self.base_manifest(level=1)
            data["workflows"] = ["planning"]
            manifest = self.write_manifest(base, data)
            with self.assertRaisesRegex(ConfigError, "Level 1"):
                load_manifest(manifest)

    def test_rejects_project_material_in_global_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            data = self.base_manifest(level=4, scope="global")
            data["project_types"] = ["software-project"]
            manifest = self.write_manifest(base, data)
            with self.assertRaisesRegex(ConfigError, "global manifest"):
                load_manifest(manifest)

    def test_rejects_manifest_adapter_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            manifest = self.write_manifest(base, self.base_manifest())
            with self.assertRaisesRegex(ConfigError, "does not match"):
                render(REPOSITORY_ROOT, "claude", base / "staging", manifest_path=manifest)


if __name__ == "__main__":
    unittest.main()
