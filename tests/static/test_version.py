import tempfile
import unittest
from pathlib import Path

from tests.support import REPOSITORY_ROOT
from tooling.verify import VerificationError, read_version


class VersionMarkerTests(unittest.TestCase):
    def test_repository_version_is_valid_semver(self):
        version = read_version(REPOSITORY_ROOT)
        self.assertRegex(version, r"^[0-9]+\.[0-9]+\.[0-9]+")

    def test_invalid_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "VERSION").write_text("v2\n", encoding="utf-8")
            with self.assertRaises(VerificationError):
                read_version(root)


if __name__ == "__main__":
    unittest.main()
