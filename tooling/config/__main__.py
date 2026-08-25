"""Command-line entry point for safe configuration tooling."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from tooling.config.composition import load_manifest
from tooling.config.diff import diff
from tooling.config.initialize import initialize
from tooling.config.paths import ConfigError
from tooling.config.render import render
from tooling.config.validate import validate


ADAPTER_CHOICES = ("codex", "claude", "gemini", "antigravity", "generic")
PROJECT_TYPE_CHOICES = (
    "software-project",
    "product-app",
    "web-app",
    "bot-service",
    "content-heavy",
    "utility-script",
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tooling.config")
    commands = parser.add_subparsers(dest="command", required=True)

    validate_parser = commands.add_parser("validate", help="validate a source repository")
    validate_parser.add_argument("--root", type=Path, required=True)

    render_parser = commands.add_parser("render", help="render one adapter into staging")
    render_parser.add_argument("--root", type=Path, required=True)
    render_parser.add_argument("--adapter")
    render_parser.add_argument("--scope", choices=("project", "global"))
    render_parser.add_argument("--manifest", type=Path)
    render_parser.add_argument("--profile", type=Path)
    render_parser.add_argument("--output-root", type=Path, required=True)

    diff_parser = commands.add_parser("diff", help="compare staging with a target")
    diff_parser.add_argument("--root", type=Path, required=True)
    diff_parser.add_argument("--adapter")
    diff_parser.add_argument("--scope", choices=("project", "global"))
    diff_parser.add_argument("--manifest", type=Path)
    diff_parser.add_argument("--profile", type=Path)
    diff_parser.add_argument("--target-root", type=Path, required=True)

    init_parser = commands.add_parser(
        "init",
        help="create a project-local adoption manifest without installing provider config",
    )
    init_parser.add_argument("--root", type=Path, required=True)
    init_parser.add_argument("--output", type=Path, required=True)
    init_parser.add_argument("--adapter", choices=ADAPTER_CHOICES)
    init_parser.add_argument("--level", type=int, choices=(1, 2, 3, 4))
    init_parser.add_argument(
        "--project-type",
        action="append",
        choices=PROJECT_TYPE_CHOICES,
        default=[],
    )
    init_parser.add_argument("--workflow", action="append", default=[])
    init_parser.add_argument("--profile-output", type=Path)
    init_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="require adapter and level instead of prompting",
    )
    return parser


def _prompt_choice(label: str, choices: Tuple[str, ...], default: str) -> str:
    print("{}:".format(label))
    for index, choice in enumerate(choices, start=1):
        suffix = " [default]" if choice == default else ""
        print("  {}. {}{}".format(index, choice, suffix))
    raw = input("> ").strip()
    if not raw:
        return default
    if raw.isdigit() and 1 <= int(raw) <= len(choices):
        return choices[int(raw) - 1]
    if raw in choices:
        return raw
    raise ConfigError("invalid selection for {}: {}".format(label, raw))


def _prompt_level() -> int:
    raw = input("Adoption level [1-4, default 1]: ").strip()
    if not raw:
        return 1
    if raw in {"1", "2", "3", "4"}:
        return int(raw)
    raise ConfigError("adoption level must be 1, 2, 3, or 4")


def _prompt_yes_no(label: str) -> bool:
    raw = input("{} [y/N]: ".format(label)).strip().lower()
    if raw in {"", "n", "no"}:
        return False
    if raw in {"y", "yes"}:
        return True
    raise ConfigError("expected yes or no")


def _resolve_render_selection(args) -> Tuple[str, str]:
    manifest = load_manifest(args.manifest) if args.manifest is not None else None
    adapter = args.adapter or (manifest["adapter"] if manifest else None)
    scope = args.scope or (manifest["scope"] if manifest else "project")
    if adapter is None:
        raise ConfigError("--adapter is required unless --manifest supplies one")
    if manifest:
        if args.adapter is not None and args.adapter != manifest["adapter"]:
            raise ConfigError("--adapter conflicts with manifest adapter")
        if args.scope is not None and args.scope != manifest["scope"]:
            raise ConfigError("--scope conflicts with manifest scope")
    return adapter, scope


def _run_init(args) -> int:
    adapter = args.adapter
    level = args.level
    project_types = list(args.project_type)
    profile_output = args.profile_output

    if args.non_interactive:
        if adapter is None or level is None:
            raise ConfigError("--non-interactive init requires --adapter and --level")
    else:
        if adapter is None:
            adapter = _prompt_choice("Provider adapter", ADAPTER_CHOICES, "codex")
        if level is None:
            level = _prompt_level()
        if level in {2, 3} and not project_types:
            selected = _prompt_choice(
                "Project type",
                PROJECT_TYPE_CHOICES,
                "software-project",
            )
            project_types = [selected]
        if profile_output is None and _prompt_yes_no("Create a personal profile template"):
            raw = input("Profile output path: ").strip()
            if not raw:
                raise ConfigError("profile output path is required after selecting yes")
            profile_output = Path(raw)

    result = initialize(
        args.root,
        args.output,
        adapter,
        level,
        project_types=project_types,
        workflows=args.workflow,
        profile_output=profile_output,
    )
    print("manifest: {}".format(result["manifest"]))
    if result["project_rules"] is not None:
        print("project rules: {}".format(result["project_rules"]))
    if result["profile"] is not None:
        print("profile: {}".format(result["profile"]))
    return 0


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
        if args.command == "init":
            return _run_init(args)
        if args.command == "render":
            adapter, scope = _resolve_render_selection(args)
            for path in render(
                args.root,
                adapter,
                args.output_root,
                scope=scope,
                manifest_path=args.manifest,
                profile_path=args.profile,
            ):
                print(path)
            return 0
        if args.command == "diff":
            adapter, scope = _resolve_render_selection(args)
            output = diff(
                args.root,
                adapter,
                args.target_root,
                scope=scope,
                manifest_path=args.manifest,
                profile_path=args.profile,
            )
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
