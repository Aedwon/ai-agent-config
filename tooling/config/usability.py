"""First-run UX helpers built on the deterministic configuration primitives."""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from tooling.config.catalog import load_adapter
from tooling.config.composition import load_manifest
from tooling.config.paths import ConfigError, resolve_beneath
from tooling.config.render import render
from tooling.config.validate import validate


PROJECT_TYPE_LABELS = {
    "software-project": "Software project",
    "product-app": "Product app",
    "web-app": "Web app",
    "bot-service": "Bot service",
    "content-heavy": "Content-heavy project",
    "utility-script": "Utility script",
}


def _read_optional_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.is_file() else ""
    except (OSError, UnicodeError):
        return ""


def detect_project_type(project_root: Path) -> Tuple[str, Tuple[str, ...]]:
    """Conservatively infer a specialized project type from strong local signals."""

    root = Path(project_root).resolve(strict=True)
    if not root.is_dir():
        raise ConfigError("project root is not a directory: {}".format(project_root))

    pubspec = root / "pubspec.yaml"
    mobile_dirs = [name for name in ("android", "ios") if (root / name).is_dir()]
    if pubspec.is_file() and mobile_dirs:
        return "product-app", tuple(["pubspec.yaml"] + [name + "/" for name in mobile_dirs])

    package_json = _read_optional_text(root / "package.json")
    python_metadata = "\n".join(
        _read_optional_text(root / name)
        for name in ("pyproject.toml", "requirements.txt", "requirements-dev.txt")
    )
    dependency_text = (package_json + "\n" + python_metadata).lower()

    bot_markers = (
        '"discord.js"',
        '"discordx"',
        "discord.py",
        "py-cord",
        "nextcord",
        "disnake",
    )
    matched_bot = next((marker for marker in bot_markers if marker in dependency_text), None)
    if matched_bot:
        return "bot-service", ("dependency: {}".format(matched_bot.strip('"')),)

    web_configs = (
        "next.config.js",
        "next.config.mjs",
        "next.config.ts",
        "vite.config.js",
        "vite.config.mjs",
        "vite.config.ts",
        "astro.config.mjs",
        "astro.config.ts",
        "svelte.config.js",
    )
    matched_configs = [name for name in web_configs if (root / name).is_file()]
    if matched_configs:
        return "web-app", tuple(matched_configs[:3])

    web_dependencies = ('"next"', '"@sveltejs/kit"', '"astro"')
    matched_web = next((marker for marker in web_dependencies if marker in package_json.lower()), None)
    if matched_web:
        return "web-app", ("dependency: {}".format(matched_web.strip('"')),)

    return "software-project", ()


def _rendered_text(
    source_root: Path,
    adapter_id: str,
    scope: str,
    manifest_path: Optional[Path],
    profile_path: Optional[Path],
) -> str:
    with tempfile.TemporaryDirectory(prefix="ai-agent-config-preview-") as directory:
        rendered_path = render(
            source_root,
            adapter_id,
            Path(directory),
            scope=scope,
            manifest_path=manifest_path,
            profile_path=profile_path,
        )[0]
        return rendered_path.read_text(encoding="utf-8")


def _reject_destination_symlinks(root: Path, destination: Path) -> None:
    relative = destination.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ConfigError(
                "apply destination contains a symlink: {}".format(relative)
            )


def _write_atomic(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=str(destination.parent),
            prefix=".ai-agent-config-apply-",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        os.replace(temporary_name, destination)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass


def apply_rendered(
    source_root: Path,
    adapter_id: str,
    target_root: Path,
    scope: str = "project",
    manifest_path: Optional[Path] = None,
    profile_path: Optional[Path] = None,
    replace: bool = False,
) -> Tuple[str, Path]:
    """Install one reviewed generated file without silently replacing drift."""

    source = Path(source_root).resolve(strict=True)
    requested_target = Path(target_root)
    if requested_target.is_symlink():
        raise ConfigError("target root cannot be a symlink: {}".format(target_root))
    try:
        target = requested_target.resolve(strict=True)
    except FileNotFoundError as error:
        raise ConfigError("target root does not exist: {}".format(target_root)) from error
    if not target.is_dir():
        raise ConfigError("target root is not a directory: {}".format(target_root))

    adapter = load_adapter(source, adapter_id)
    try:
        output_path = adapter.path_for(scope)
    except ValueError as error:
        raise ConfigError(str(error)) from error
    destination = resolve_beneath(target, output_path, must_exist=False, label="target path")
    _reject_destination_symlinks(target, destination)
    if destination.is_symlink():
        raise ConfigError("target path cannot be a symlink: {}".format(output_path))
    if destination.exists() and not destination.is_file():
        raise ConfigError("target path is not a regular file: {}".format(output_path))

    rendered = _rendered_text(source, adapter_id, scope, manifest_path, profile_path)
    existed = destination.exists()
    if existed:
        try:
            current = destination.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ConfigError("cannot read target path: {}".format(error)) from error
        if current == rendered:
            return "unchanged", destination
        if not replace:
            raise ConfigError(
                "refusing to replace existing {} without --replace".format(output_path)
            )

    _write_atomic(destination, rendered)
    return ("replaced" if existed else "created"), destination


def create_profile_template(source_root: Path, output: Path) -> Path:
    """Create an optional private profile template outside the source repository."""

    source = Path(source_root).resolve(strict=True)
    errors = validate(source)
    if errors:
        raise ConfigError("repository validation failed:\n{}".format("\n".join(errors)))
    destination = Path(output).resolve(strict=False)
    try:
        destination.relative_to(source)
    except ValueError:
        pass
    else:
        raise ConfigError("profile output must be outside the ai-agent-config source root")
    if destination.exists() or destination.is_symlink():
        raise ConfigError("refusing to overwrite existing path: {}".format(destination))
    template = (source / "profiles" / "example.md").read_text(encoding="utf-8")
    _write_atomic(destination, template)
    return destination


def doctor(
    source_root: Path,
    project_root: Path,
    manifest_path: Optional[Path] = None,
    profile_path: Optional[Path] = None,
) -> Tuple[bool, List[Tuple[str, str]]]:
    """Check whether one project installation matches its canonical configuration."""

    source = Path(source_root).resolve(strict=True)
    project = Path(project_root).resolve(strict=True)
    checks: List[Tuple[str, str]] = []

    errors = validate(source)
    if errors:
        return False, [("error", "Source configuration invalid: {}".format(errors[0]))]
    checks.append(("ok", "Source configuration valid"))

    selected_manifest = Path(manifest_path) if manifest_path is not None else project / "ai-agent-config.json"
    if not selected_manifest.is_file():
        checks.append(("error", "Manifest missing: {}".format(selected_manifest)))
        return False, checks
    manifest = load_manifest(selected_manifest)
    checks.append(("ok", "Manifest valid"))

    adapter = load_adapter(source, manifest["adapter"])
    output_path = adapter.path_for(manifest["scope"])
    checks.append(("ok", "Provider: {}".format(adapter.label)))

    project_rules = manifest.get("project_rules")
    if project_rules:
        rules_path = selected_manifest.parent / project_rules
        if rules_path.is_file() and not rules_path.is_symlink():
            checks.append(("ok", "Project rules found"))
        else:
            checks.append(("error", "Project rules missing: {}".format(project_rules)))

    target = resolve_beneath(project, output_path, must_exist=False, label="target path")
    if not target.is_file() or target.is_symlink():
        checks.append(("error", "Generated provider file missing: {}".format(output_path)))
        return False, checks

    rendered = _rendered_text(
        source,
        manifest["adapter"],
        manifest["scope"],
        selected_manifest,
        profile_path,
    )
    try:
        installed = target.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ConfigError("cannot read installed provider file: {}".format(error)) from error
    if installed != rendered:
        checks.append(("error", "Generated provider file differs: {}".format(output_path)))
        return False, checks
    checks.append(("ok", "Generated provider file is current: {}".format(output_path)))

    types = manifest.get("project_types", [])
    if types:
        specialized = [value for value in types if value != "software-project"]
        selected = specialized[-1] if specialized else "software-project"
        checks.append(("ok", "Project type: {}".format(PROJECT_TYPE_LABELS.get(selected, selected))))
    return True, checks
