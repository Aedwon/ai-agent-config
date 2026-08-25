"""Command-line entry point for safe configuration tooling."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from tooling.config.diff import diff
from tooling.config.paths import ConfigError
from tooling.config.render import render
from tooling.config.validate import validate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tooling.config")
    commands = parser.add_subparsers(dest="command", required=True)

    validate_parser = commands.add_parser("validate", help="validate a source repository")
    validate_parser.add_argument("--root", type=Path, required=True)

    render_parser = commands.add_parser("render", help="render one adapter into staging")
    render_parser.add_argument("--root", type=Path, required=True)
    render_parser.add_argument("--adapter", required=True)
    render_parser.add_argument("--scope", choices=("project", "global"), default="project")
    render_parser.add_argument("--output-root", type=Path, required=True)

    diff_parser = commands.add_parser("diff", help="compare staging with a target")
    diff_parser.add_argument("--root", type=Path, required=True)
    diff_parser.add_argument("--adapter", required=True)
    diff_parser.add_argument("--scope", choices=("project", "global"), default="project")
    diff_parser.add_argument("--target-root", type=Path, required=True)
    return parser


def main(arguments: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(arguments)
    try:
        if args.command == "validate":
            errors = validate(args.root)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("OK")
            return 0
        if args.command == "render":
            for path in render(args.root, args.adapter, args.output_root, scope=args.scope):
                print(path)
            return 0
        if args.command == "diff":
            output = diff(args.root, args.adapter, args.target_root, scope=args.scope)
            if output:
                sys.stdout.write(output)
                return 1
            return 0
    except (ConfigError, OSError, UnicodeError) as error:
        print(error, file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
