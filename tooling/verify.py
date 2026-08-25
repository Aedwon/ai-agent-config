"""Run the repository's local and CI self-verification checks."""

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


class VerificationError(ValueError):
    """Raised when repository verification metadata is invalid."""


def read_version(root: Path) -> str:
    """Read and validate the repository's SemVer marker."""

    version_path = Path(root) / "VERSION"
    try:
        value = version_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as error:
        raise VerificationError("cannot read VERSION: {}".format(error)) from error
    if not VERSION_PATTERN.fullmatch(value):
        raise VerificationError("VERSION must contain one semantic version, found {!r}".format(value))
    return value


def _run(root: Path, command: List[str]) -> int:
    print("$ {}".format(shlex.join(command)))
    completed = subprocess.run(command, cwd=str(root), check=False)
    return completed.returncode


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tooling.verify")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="repository root to verify",
    )
    parser.add_argument(
        "--diff-base",
        help="optional Git ref/SHA used for a three-dot whitespace check against HEAD",
    )
    return parser


def main(arguments: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(arguments)
    try:
        root = Path(args.root).resolve(strict=True)
        if not root.is_dir():
            raise VerificationError("repository root is not a directory: {}".format(root))
        version = read_version(root)
    except (OSError, VerificationError) as error:
        print(error, file=sys.stderr)
        return 1

    print("AI Agent Config v{}".format(version))

    if args.diff_base:
        diff_checks = [["git", "diff", "--check", "{}...HEAD".format(args.diff_base)]]
    else:
        diff_checks = [
            ["git", "diff", "--check"],
            ["git", "diff", "--cached", "--check"],
        ]

    commands = diff_checks + [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        [sys.executable, "-m", "tooling.config", "validate", "--root", "."],
    ]

    for command in commands:
        if _run(root, command) != 0:
            print("Verification failed.", file=sys.stderr)
            return 1

    print("Verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
