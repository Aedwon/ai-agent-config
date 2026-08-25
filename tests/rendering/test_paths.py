import tempfile
import unittest
from pathlib import Path


class PathSafetyTests(unittest.TestCase):
    def load_api(self):
        try:
            from tooling.config.paths import (
                ConfigError,
                prepare_output_root,
                resolve_beneath,
                safe_relative_path,
            )
        except ModuleNotFoundError as error:
            self.fail("path-safety API is missing: {}".format(error))
        return ConfigError, prepare_output_root, resolve_beneath, safe_relative_path

    def test_resolves_safe_relative_path_beneath_root(self):
        _, _, resolve_beneath, _ = self.load_api()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            expected = root.resolve() / "nested" / "file.md"

            actual = resolve_beneath(root, "nested/file.md")

            self.assertEqual(actual, expected)

    def test_rejects_absolute_traversing_and_backslash_paths(self):
        ConfigError, _, _, safe_relative_path = self.load_api()

        for unsafe in ("/outside.md", "../outside.md", "a/../../outside.md", "a\\outside.md"):
            with self.subTest(path=unsafe):
                with self.assertRaises(ConfigError):
                    safe_relative_path(unsafe, "fixture path")

    def test_rejects_source_symlink_that_escapes_root(self):
        ConfigError, _, resolve_beneath, _ = self.load_api()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            (outside / "policy.md").write_text("outside", encoding="utf-8")
            (root / "linked").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ConfigError, "escapes"):
                resolve_beneath(root, "linked/policy.md", must_exist=True)

    def test_rejects_missing_required_source(self):
        ConfigError, _, resolve_beneath, _ = self.load_api()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            with self.assertRaisesRegex(ConfigError, "does not exist"):
                resolve_beneath(root, "missing.md", must_exist=True)

    def test_rejects_output_root_inside_source(self):
        ConfigError, prepare_output_root, _, _ = self.load_api()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            source.mkdir()

            with self.assertRaisesRegex(ConfigError, "outside the source root"):
                prepare_output_root(source, source / "build")

    def test_rejects_symlink_output_root(self):
        ConfigError, prepare_output_root, _, _ = self.load_api()
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "source"
            real_output = base / "real-output"
            linked_output = base / "linked-output"
            source.mkdir()
            real_output.mkdir()
            linked_output.symlink_to(real_output, target_is_directory=True)

            with self.assertRaisesRegex(ConfigError, "symlink"):
                prepare_output_root(source, linked_output)


if __name__ == "__main__":
    unittest.main()
