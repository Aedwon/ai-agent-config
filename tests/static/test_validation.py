import json
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT, copy_repository


class RepositoryValidationTests(unittest.TestCase):
    def validate(self, root: Path):
        try:
            from tooling.config.validate import validate
        except ModuleNotFoundError as error:
            self.fail("repository validator is missing: {}".format(error))
        return validate(root)

    def assert_error_contains(self, errors, expected):
        self.assertTrue(
            any(expected in error for error in errors),
            "expected {!r} in validation errors:\n{}".format(
                expected, "\n".join(errors)
            ),
        )

    def test_accepts_current_v2_repository(self):
        self.assertEqual(self.validate(REPOSITORY_ROOT), [])

    def test_rejects_runtime_name_in_universal_core(self):
        root = copy_repository(self)
        core = root / "core" / "agent-contract.md"
        core.write_text(core.read_text(encoding="utf-8") + "\nCodex\n", encoding="utf-8")

        errors = self.validate(root)

        self.assert_error_contains(errors, "core/agent-contract.md: forbidden universal term 'Codex'")

    def test_rejects_unknown_catalog_strategy(self):
        root = copy_repository(self)
        catalog_path = root / "skills" / "catalog.yaml"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["entries"][0]["strategy"] = "vendored_copy"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

        errors = self.validate(root)

        self.assert_error_contains(errors, "strategy must be exactly one of")

    def test_rejects_adaptation_without_retained_license(self):
        root = copy_repository(self)
        (root / "LICENSES" / "matt-pocock-skills-MIT.txt").unlink()

        errors = self.validate(root)

        self.assert_error_contains(errors, "adapted license file does not exist")

    def test_rejects_duplicate_automatic_trigger_owner(self):
        root = copy_repository(self)
        catalog_path = root / "skills" / "catalog.yaml"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        automatic = [
            entry
            for entry in catalog["entries"]
            if entry["trigger"]["mode"] == "package-managed"
        ]
        automatic[1]["trigger"]["owner"] = automatic[0]["trigger"]["owner"]
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")

        errors = self.validate(root)

        self.assert_error_contains(errors, "duplicate automatic trigger owner")

    def test_rejects_adapter_path_traversal(self):
        root = copy_repository(self)
        adapter_path = root / "adapters" / "codex" / "adapter.json"
        adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
        adapter["output"]["path"] = "../AGENTS.md"
        adapter["discovery"]["project_path"] = "../AGENTS.md"
        adapter_path.write_text(json.dumps(adapter), encoding="utf-8")

        errors = self.validate(root)

        self.assert_error_contains(errors, "must stay below its declared root")

    def test_rejects_forbidden_adapter_destination_category(self):
        root = copy_repository(self)
        adapter_path = root / "adapters" / "codex" / "adapter.json"
        adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
        adapter["output"]["path"] = ".cache/generated-policy.md"
        adapter["discovery"]["project_path"] = ".cache/generated-policy.md"
        adapter_path.write_text(json.dumps(adapter), encoding="utf-8")

        errors = self.validate(root)

        self.assert_error_contains(errors, "forbidden destination category")

    def test_rejects_adapter_template_symlink_escape(self):
        root = copy_repository(self)
        template = root / "adapters" / "codex" / "entry.md.tmpl"
        outside = root.parent / "outside-template.md"
        outside.write_text("{{CONTENT}}\n", encoding="utf-8")
        template.unlink()
        template.symlink_to(outside)

        errors = self.validate(root)

        self.assert_error_contains(errors, "escapes its declared root")

    def test_rejects_unresolved_placeholder_in_managed_content(self):
        root = copy_repository(self)
        workflow = root / "workflows" / "design.md"
        workflow.write_text(
            workflow.read_text(encoding="utf-8") + "\n{{UNRESOLVED}}\n",
            encoding="utf-8",
        )

        errors = self.validate(root)

        self.assert_error_contains(errors, "unresolved placeholder '{{UNRESOLVED}}'")

    def test_rejects_machine_private_absolute_path(self):
        root = copy_repository(self)
        workflow = root / "workflows" / "design.md"
        workflow.write_text(
            workflow.read_text(encoding="utf-8") + "\n/Users/example/private\n",
            encoding="utf-8",
        )

        errors = self.validate(root)

        self.assert_error_contains(errors, "machine-private absolute path")

    def test_rejects_authorization_fixture_that_grants_edit_from_plan(self):
        root = copy_repository(self)
        cases_path = root / "tests" / "fixtures" / "authorization-cases.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
        plan_case = next(case for case in cases["cases"] if case["request"] == "write an implementation plan")
        plan_case["authorized"] = True
        cases_path.write_text(json.dumps(cases), encoding="utf-8")

        errors = self.validate(root)

        self.assert_error_contains(errors, "non-mutating request grants mutation")

    def test_rejects_adapter_missing_required_field(self):
        root = copy_repository(self)
        adapter_path = root / "adapters" / "codex" / "adapter.json"
        adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
        del adapter["label"]
        adapter_path.write_text(json.dumps(adapter), encoding="utf-8")

        errors = self.validate(root)

        self.assert_error_contains(errors, "missing required field 'label'")


if __name__ == "__main__":
    unittest.main()
