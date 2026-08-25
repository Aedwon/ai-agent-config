import shutil
import tempfile
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def copy_repository(test_case):
    temporary_directory = tempfile.TemporaryDirectory()
    test_case.addCleanup(temporary_directory.cleanup)
    destination = Path(temporary_directory.name) / "repository"
    shutil.copytree(
        REPOSITORY_ROOT,
        destination,
        ignore=shutil.ignore_patterns(
            ".git",
            ".worktrees",
            ".v2-implementation-plan.md",
            "__pycache__",
            "*.pyc",
        ),
    )
    return destination
