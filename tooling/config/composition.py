"""Compose canonical policy with explicitly selected project material."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from tooling.config.paths import ConfigError, resolve_beneath, safe_relative_path


NAME = re.compile(r"^[a-z][a-z0-9-]*$")
MANIFEST_KEYS = {
    "version",
    "level",
    "adapter",
    "scope",
    "output",
    "components",
    "project_rules",
    "project_types",
    "workflows",
    "external_skills",
    "optional_skills",
    "isolation",
    "global_configuration",
}
CANONICAL_SOURCES = {
    "project": (
        "core/precedence.md",
        "core/agent-contract.md",
        "templates/minimal/AGENT_RULES.md",
    ),
    "global": (
        "core/precedence.md",
        "core/agent-contract.md",
    ),
}


def _markdown_body(text: str) -> str:
    if not text.startswith("---\n"):
        return text.strip()
    closing = text.find("\n---\n", 4)
    if closing == -1:
        raise ConfigError("canonical Markdown has unterminated frontmatter")
    return text[closing + 5 :].strip()


def _read_utf8(path: Path, label: str, strip_frontmatter: bool = False) -> str:
    if path.is_symlink():
        raise ConfigError("{} cannot be a symlink: {}".format(label, path))
    if not path.is_file():
        raise ConfigError("{} is not a regular file: {}".format(label, path))
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ConfigError("cannot read {}: {}".format(label, error)) from error
    return _markdown_body(text) if strip_frontmatter else text.strip()


def _list_of_names(value: Any, label: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError("{} must be an array".format(label))
    names: List[str] = []
    for item in value:
        if not isinstance(item, str) or not NAME.fullmatch(item):
            raise ConfigError("{} contains an invalid name: {!r}".format(label, item))
        if item in names:
            raise ConfigError("{} contains duplicate name '{}'".format(label, item))
        names.append(item)
    return names


def load_manifest(path: Path) -> Dict[str, Any]:
    """Load and validate one user-selected adoption manifest."""

    requested = Path(path)
    if requested.is_symlink():
        raise ConfigError("manifest cannot be a symlink: {}".format(path))
    try:
        resolved = requested.resolve(strict=True)
    except FileNotFoundError as error:
        raise ConfigError("manifest does not exist: {}".format(path)) from error
    if not resolved.is_file():
        raise ConfigError("manifest is not a regular file: {}".format(path))
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConfigError("manifest is not valid UTF-8 JSON: {}".format(error)) from error
    if not isinstance(data, dict):
        raise ConfigError("manifest must contain a JSON object")

    extra = sorted(set(data) - MANIFEST_KEYS)
    if extra:
        raise ConfigError("manifest contains unsupported field '{}'".format(extra[0]))
    if data.get("version") != 1:
        raise ConfigError("manifest version must be 1")
    level = data.get("level")
    if level not in {1, 2, 3, 4}:
        raise ConfigError("manifest level must be 1, 2, 3, or 4")
    adapter = data.get("adapter")
    if not isinstance(adapter, str) or not NAME.fullmatch(adapter):
        raise ConfigError("manifest adapter is invalid")
    scope = data.get("scope")
    expected_scope = "global" if level == 4 else "project"
    if scope != expected_scope:
        raise ConfigError(
            "manifest level {} must use scope '{}'".format(level, expected_scope)
        )

    project_types = _list_of_names(data.get("project_types"), "manifest project_types")
    workflows = _list_of_names(data.get("workflows"), "manifest workflows")
    project_rules = data.get("project_rules")
    if project_rules is not None:
        if not isinstance(project_rules, str):
            raise ConfigError("manifest project_rules must be a relative path")
        safe_relative_path(project_rules, "manifest project_rules")

    if level == 1 and (project_rules or project_types or workflows):
        raise ConfigError("Level 1 manifest cannot select project rules, project types, or workflows")
    if scope == "global" and (project_rules or project_types or workflows):
        raise ConfigError("global manifest cannot select project-only material")

    normalized = dict(data)
    normalized["project_types"] = project_types
    normalized["workflows"] = workflows
    normalized["_path"] = str(resolved)
    return normalized


def _source_section(root: Path, relative: str, label: str, strip_frontmatter: bool = False) -> str:
    path = resolve_beneath(root, relative, must_exist=True, label=label)
    return _read_utf8(path, label, strip_frontmatter=strip_frontmatter)


def _external_relative_section(manifest: Dict[str, Any], relative: str, label: str) -> str:
    manifest_path = Path(manifest["_path"])
    project_root = manifest_path.parent
    path = resolve_beneath(project_root, relative, must_exist=True, label=label)
    return _read_utf8(path, label)


def compose_bundle(
    root: Path,
    scope: str = "project",
    manifest_path: Optional[Path] = None,
    profile_path: Optional[Path] = None,
) -> str:
    """Build one deterministic instruction bundle from explicit selections."""

    if scope not in CANONICAL_SOURCES:
        raise ConfigError("scope must be project or global")

    sections: List[str] = []
    for relative in CANONICAL_SOURCES[scope]:
        sections.append(
            _source_section(
                root,
                relative,
                relative,
                strip_frontmatter=relative.startswith("core/"),
            )
        )

    manifest: Optional[Dict[str, Any]] = None
    if manifest_path is not None:
        manifest = load_manifest(Path(manifest_path))
        if manifest["scope"] != scope:
            raise ConfigError(
                "manifest scope '{}' does not match render scope '{}'".format(
                    manifest["scope"], scope
                )
            )

        project_rules = manifest.get("project_rules")
        if project_rules:
            sections.append(
                _external_relative_section(manifest, project_rules, "project rules")
            )
        for project_type in manifest["project_types"]:
            sections.append(
                _source_section(
                    root,
                    "project-types/{}.md".format(project_type),
                    "project type '{}'".format(project_type),
                )
            )
        for workflow in manifest["workflows"]:
            sections.append(
                _source_section(
                    root,
                    "workflows/{}.md".format(workflow),
                    "workflow '{}'".format(workflow),
                )
            )

    if profile_path is not None:
        requested_profile = Path(profile_path)
        try:
            resolved_profile = requested_profile.resolve(strict=True)
        except FileNotFoundError as error:
            raise ConfigError("profile does not exist: {}".format(profile_path)) from error
        sections.append(_read_utf8(resolved_profile, "profile"))

    return "\n\n---\n\n".join(section for section in sections if section) + "\n"
