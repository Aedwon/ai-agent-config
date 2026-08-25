"""Command-line entry point for safe configuration tooling."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from tooling.config.catalog import load_adapter
from tooling.config.composition import load_manifest
from tooling.config.diff import diff
from tooling.config.initialize import initialize
from tooling.config.paths import ConfigError, resolve_beneath
from tooling.config.render import render
from tooling.config.usability import (
    PROJECT_TYPE_LABELS,
    apply_rendered,
    create_profile_template,
    detect_project_type,
    doctor,
)
from tooling.config.validate import validate


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
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

    setup_parser = commands.add_parser(
        "setup",
        help="guided first-run setup for one project",
    )
    setup_parser.add_argument("project", type=Path)
    setup_parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    setup_parser.add_argument("--adapter", choices=ADAPTER_CHOICES)
    setup_parser.add_argument("--level", type=int, choices=(1, 2, 3, 4))
    setup_parser.add_argument(
        "--project-type",
        action="append",
        choices=PROJECT_TYPE_CHOICES,
        default=[],
    )
    setup_parser.add_argument(
        "--advanced",
        action="store_true",
        help="show adoption-level selection instead of recommending Level 2",
    )
    setup_parser.add_argument(
        "--yes",
        action="store_true",
        help="accept non-destructive defaults and install without prompting",
    )
    setup_parser.add_argument(
        "--no-apply",
        action="store_true",
        help="create project configuration without installing the provider file",
    )
    setup_parser.add_argument(
        "--preview",
        action="store_true",
        help="print the generated provider-file diff before applying",
    )
    setup_parser.add_argument(
        "--replace",
        action="store_true",
        help="allow an explicitly confirmed existing provider file to be replaced",
    )

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

    apply_parser = commands.add_parser(
        "apply",
        help="install one rendered provider file after review or explicit confirmation",
    )
    apply_parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    apply_parser.add_argument("--manifest", type=Path, required=True)
    apply_parser.add_argument("--profile", type=Path)
    apply_parser.add_argument("--target-root", type=Path, required=True)
    apply_parser.add_argument("--replace", action="store_true")
    apply_parser.add_argument("--yes", action="store_true")

    doctor_parser = commands.add_parser(
        "doctor",
        help="check whether a project installation is current",
    )
    doctor_parser.add_argument("project", type=Path)
    doctor_parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    doctor_parser.add_argument("--manifest", type=Path)
    doctor_parser.add_argument("--profile", type=Path)

    profile_parser = commands.add_parser(
        "profile",
        help="create an optional personal profile template",
    )
    profile_parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    profile_parser.add_argument("--output", type=Path, required=True)

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
    print("Setup mode:")
    print("  1. Minimal — first trial, tiny repository, or low-coordination work")
    print("  2. Normal — recommended for most repositories [default]")
    print("  3. Agent-heavy — several agents, long-running work, or costly changes")
    print("  4. Provider-native/global — explicit global configuration")
    raw = input("> ").strip()
    if not raw:
        return 2
    if raw in {"1", "2", "3", "4"}:
        return int(raw)
    raise ConfigError("setup mode must be 1, 2, 3, or 4")


def _prompt_yes_no(label: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    raw = input(label + suffix).strip().lower()
    if not raw:
        return default
    if raw in {"y", "yes"}:
        return True
    if raw in {"n", "no"}:
        return False
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


def _specialized_project_type(project_types: List[str]) -> str:
    specialized = [value for value in project_types if value != "software-project"]
    return specialized[-1] if specialized else "software-project"


def _print_configuration_summary(root: Path, manifest_path: Path) -> None:
    manifest = load_manifest(manifest_path)
    adapter = load_adapter(Path(root).resolve(strict=True), manifest["adapter"])
    selected_type = _specialized_project_type(list(manifest.get("project_types", [])))
    print("\nConfiguration")
    print("  Provider       {}".format(adapter.label))
    print("  Setup          {}".format({1: "Minimal", 2: "Normal", 3: "Agent-heavy", 4: "Global"}[manifest["level"]]))
    if manifest["level"] in {2, 3}:
        print("  Project type   {}".format(PROJECT_TYPE_LABELS.get(selected_type, selected_type)))
    print("  Output         {}".format(manifest["output"]))


def _run_init(args) -> int:
    adapter = args.adapter
    level = args.level
    project_types = list(args.project_type)

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

    result = initialize(
        args.root,
        args.output,
        adapter,
        level,
        project_types=project_types,
        workflows=args.workflow,
        profile_output=args.profile_output,
    )
    _print_configuration_summary(args.root, result["manifest"])
    print("\nCreated")
    print("  {}".format(result["manifest"]))
    if result["project_rules"] is not None:
        print("  {}".format(result["project_rules"]))
    if result["profile"] is not None:
        print("  {}".format(result["profile"]))
    print("\nNo provider file was installed.")
    return 0


def _run_setup(args) -> int:
    source_root = Path(args.root).resolve(strict=True)
    project = Path(args.project).resolve(strict=True)
    if not project.is_dir():
        raise ConfigError("project root is not a directory: {}".format(args.project))
    if args.yes and args.adapter is None:
        raise ConfigError("--yes setup requires --adapter so provider selection is explicit")

    print("AI Agent Config")
    print("\nProject")
    print("  {}".format(project))

    adapter_id = args.adapter or _prompt_choice("Provider", ADAPTER_CHOICES, "codex")

    if args.level is not None:
        level = args.level
    elif args.advanced:
        level = _prompt_level()
    else:
        level = 2
        if not args.yes:
            print("\nSetup")
            print("  Normal (recommended for most software repositories)")

    project_types = list(args.project_type)
    if level in {2, 3} and not project_types:
        detected, evidence = detect_project_type(project)
        if args.advanced and not args.yes:
            print("\nDetected project type")
            print("  {}".format(PROJECT_TYPE_LABELS[detected]))
            if evidence:
                print("  Based on: {}".format(", ".join(evidence)))
            selected = _prompt_choice("Project type", PROJECT_TYPE_CHOICES, detected)
            project_types = [selected]
        else:
            project_types = [detected]
            print("\nProject type")
            if detected == "software-project":
                print("  Software project (safe default; no specialized type detected)")
            else:
                print("  {}".format(PROJECT_TYPE_LABELS[detected]))
                if evidence:
                    print("  Based on: {}".format(", ".join(evidence)))

    adapter = load_adapter(source_root, adapter_id)
    scope = "global" if level == 4 else "project"
    output_path = adapter.path_for(scope)
    manifest_path = project / "ai-agent-config.json"

    print("\nPlan")
    print("  Provider       {}".format(adapter.label))
    print("  Setup          {}".format({1: "Minimal", 2: "Normal", 3: "Agent-heavy", 4: "Global"}[level]))
    if level in {2, 3}:
        selected_type = _specialized_project_type(project_types)
        print("  Project type   {}".format(PROJECT_TYPE_LABELS.get(selected_type, selected_type)))
    print("  Manifest       {}".format(manifest_path))
    if level in {2, 3}:
        print("  Project rules  {}".format(project / "PROJECT_RULES.md"))
    if scope == "global":
        print("  Provider file  configuration-only in guided setup")
    elif args.no_apply:
        print("  Provider file  not installed (--no-apply)")
    else:
        print("  Provider file  {}".format(project / output_path))

    if not args.yes:
        action = (
            "Create project configuration?"
            if args.no_apply or scope == "global"
            else "Create and install this configuration?"
        )
        if not _prompt_yes_no(action, default=True):
            print("\nNo changes made.")
            return 0

    result = initialize(
        source_root,
        manifest_path,
        adapter_id,
        level,
        project_types=project_types,
    )
    print("\nCreated")
    print("  {}".format(result["manifest"]))
    if result["project_rules"] is not None:
        print("  {}".format(result["project_rules"]))

    manifest = load_manifest(manifest_path)
    if manifest["scope"] == "global":
        print("\nGlobal/provider-native setup is configuration-only here.")
        print("Use render and diff with an explicit global target after review.")
        return 0

    target_path = resolve_beneath(project, output_path, must_exist=False, label="target path")
    changes = diff(
        source_root,
        manifest["adapter"],
        project,
        scope=manifest["scope"],
        manifest_path=manifest_path,
    )

    previewed = False
    if changes and args.preview:
        print("\n" + changes.rstrip("\n"))
        previewed = True

    if args.no_apply:
        print("\nProvider file was not installed (--no-apply).")
        return 0

    replace = args.replace
    if target_path.exists() and not changes:
        print("\nAlready current: {}".format(target_path))
        return 0
    if target_path.exists() and changes and not replace:
        if args.yes:
            raise ConfigError(
                "{} already exists; rerun with --replace to authorize replacement".format(output_path)
            )
        if not previewed:
            print("\n" + changes.rstrip("\n"))
        print("\n{} already exists and will not be overwritten automatically.".format(output_path))
        if not _prompt_yes_no("Replace it with the rendered configuration?", default=False):
            print("\nProvider file was not changed.")
            return 0
        replace = True
    elif target_path.exists() and changes and replace and not args.yes:
        if not previewed:
            print("\n" + changes.rstrip("\n"))
        if not _prompt_yes_no("Apply replacement?", default=False):
            print("\nProvider file was not changed.")
            return 0

    status, installed_path = apply_rendered(
        source_root,
        manifest["adapter"],
        project,
        scope=manifest["scope"],
        manifest_path=manifest_path,
        replace=replace,
    )
    if status == "unchanged":
        print("\nAlready current: {}".format(installed_path))
    else:
        print("\nInstalled AI Agent Config")
        print("  {}".format(installed_path))
    print("\nCheck this installation anytime with:")
    print("  python3 -m tooling.config doctor {}".format(project))
    print("\nOptional personal preferences:")
    print("  python3 -m tooling.config profile --output /explicit/private/profile.md")
    return 0


def _run_apply(args) -> int:
    source_root = Path(args.root).resolve(strict=True)
    manifest = load_manifest(args.manifest)
    adapter = load_adapter(source_root, manifest["adapter"])
    output_path = adapter.path_for(manifest["scope"])
    target_root = Path(args.target_root).resolve(strict=True)
    target_path = resolve_beneath(target_root, output_path, must_exist=False, label="target path")
    changes = diff(
        source_root,
        manifest["adapter"],
        target_root,
        scope=manifest["scope"],
        manifest_path=args.manifest,
        profile_path=args.profile,
    )
    if not changes:
        print("Already current: {}".format(target_path))
        return 0

    replace = args.replace
    if not args.yes:
        print(changes.rstrip("\n"))
        if target_path.exists():
            if not replace:
                print("\nExisting {} will not be overwritten automatically.".format(output_path))
                replace = _prompt_yes_no("Replace it?", default=False)
                if not replace:
                    print("No changes applied.")
                    return 0
            elif not _prompt_yes_no("Apply replacement?", default=False):
                print("No changes applied.")
                return 0
        elif not _prompt_yes_no("Create {}?".format(output_path), default=True):
            print("No changes applied.")
            return 0

    status, path = apply_rendered(
        source_root,
        manifest["adapter"],
        target_root,
        scope=manifest["scope"],
        manifest_path=args.manifest,
        profile_path=args.profile,
        replace=replace,
    )
    print("{}: {}".format(status.capitalize(), path))
    return 0


def _run_doctor(args) -> int:
    healthy, checks = doctor(
        args.root,
        args.project,
        manifest_path=args.manifest,
        profile_path=args.profile,
    )
    print("AI Agent Config doctor\n")
    for status, message in checks:
        print("[{}] {}".format("ok" if status == "ok" else "error", message))
    print("\n{}".format("Configuration is ready." if healthy else "Configuration needs attention."))
    return 0 if healthy else 1


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
        if args.command == "setup":
            return _run_setup(args)
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
        if args.command == "apply":
            return _run_apply(args)
        if args.command == "doctor":
            return _run_doctor(args)
        if args.command == "profile":
            path = create_profile_template(args.root, args.output)
            print("Created profile template: {}".format(path))
            return 0
    except (ConfigError, OSError, UnicodeError) as error:
        print(error, file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
