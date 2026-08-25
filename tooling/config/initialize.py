"""Explicit, project-local initialization for adoption manifests."""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from tooling.config.catalog import load_adapter
from tooling.config.paths import ConfigError
from tooling.config.validate import validate


PROJECT_TYPES = {
    "software-project",
    "product-app",
    "web-app",
    "bot-service",
    "content-heavy",
    "utility-script",
}
WORKFLOWS = {
    "design",
    "planning",
    "implementation",
    "debugging",
    "delegation",
    "code-review",
    "verification",
    "grilling",
    "handoff",
    "decision-recording",
}
DEFAULT_WORKFLOWS = {
    1: (),
    2: ("planning", "implementation", "verification"),
    3: ("planning", "implementation", "delegation", "code-review", "verification", "handoff"),
    4: (),
}


def _is_beneath(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _write_new(path: Path, content: str) -> None:
    if path.exists() or path.is_symlink():
        raise ConfigError("refusing to overwrite existing path: {}".format(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=str(path.parent),
            prefix=".ai-agent-config-init-",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = handle.name
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                Path(temporary).unlink()
            except FileNotFoundError:
                pass


def _normalize_project_types(level: int, values: Iterable[str]) -> List[str]:
    requested = list(values)
    if level not in {2, 3}:
        if requested:
            raise ConfigError("project types are valid only for Level 2 or Level 3")
        return []
    if not requested:
        return ["software-project"]
    for value in requested:
        if value not in PROJECT_TYPES:
            raise ConfigError("unknown project type '{}'".format(value))
    if "software-project" not in requested:
        requested.insert(0, "software-project")
    return list(dict.fromkeys(requested))


def _normalize_workflows(level: int, values: Iterable[str]) -> List[str]:
    requested = list(values) or list(DEFAULT_WORKFLOWS[level])
    if level in {1, 4} and requested:
        raise ConfigError("workflows are valid only for Level 2 or Level 3")
    for value in requested:
        if value not in WORKFLOWS:
            raise ConfigError("unknown workflow '{}'".format(value))
    return list(dict.fromkeys(requested))


def initialize(
    root: Path,
    output: Path,
    adapter_id: str,
    level: int,
    project_types: Iterable[str] = (),
    workflows: Iterable[str] = (),
    profile_output: Optional[Path] = None,
) -> Dict[str, Optional[Path]]:
    """Create project-owned setup files without installing provider config."""

    source_root = Path(root).resolve(strict=True)
    errors = validate(source_root)
    if errors:
        raise ConfigError("repository validation failed:\n{}".format("\n".join(errors)))
    adapter = load_adapter(source_root, adapter_id)
    if level not in {1, 2, 3, 4}:
        raise ConfigError("level must be 1, 2, 3, or 4")

    output_path = Path(output).resolve(strict=False)
    if output_path == source_root or _is_beneath(output_path, source_root):
        raise ConfigError("init output must be outside the ai-agent-config source root")
    if output_path.exists() or output_path.is_symlink():
        raise ConfigError("refusing to overwrite existing path: {}".format(output_path))

    selected_types = _normalize_project_types(level, project_types)
    selected_workflows = _normalize_workflows(level, workflows)
    scope = "global" if level == 4 else "project"

    project_rules_path: Optional[Path] = None
    if level in {2, 3}:
        project_rules_path = output_path.parent / "PROJECT_RULES.md"
        if project_rules_path.is_symlink():
            raise ConfigError("project rules cannot be a symlink: {}".format(project_rules_path))
        if project_rules_path.exists() and not project_rules_path.is_file():
            raise ConfigError("project rules path is not a regular file: {}".format(project_rules_path))

    created_profile: Optional[Path] = None
    if profile_output is not None:
        created_profile = Path(profile_output).resolve(strict=False)
        if created_profile == source_root or _is_beneath(created_profile, source_root):
            raise ConfigError("profile output must be outside the ai-agent-config source root")
        if created_profile.exists() or created_profile.is_symlink():
            raise ConfigError("refusing to overwrite existing path: {}".format(created_profile))

    manifest = {
        "version": 1,
        "level": level,
        "scope": scope,
        "adapter": adapter_id,
        "output": adapter.path_for(scope),
        "project_types": selected_types,
        "workflows": selected_workflows,
        "external_skills": False if level == 1 else "optional",
        "global_configuration": level == 4,
    }
    if project_rules_path is not None:
        manifest["project_rules"] = "PROJECT_RULES.md"

    if project_rules_path is not None and not project_rules_path.exists():
        template = source_root / "templates" / "project" / "PROJECT_RULES.md"
        _write_new(project_rules_path, template.read_text(encoding="utf-8"))

    if created_profile is not None:
        profile_template = source_root / "profiles" / "example.md"
        _write_new(created_profile, profile_template.read_text(encoding="utf-8"))

    _write_new(output_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    return {
        "manifest": output_path,
        "project_rules": project_rules_path,
        "profile": created_profile,
    }
