"""Deterministic rendering into an explicit staging root."""

import os
import re
import tempfile
from pathlib import Path
from typing import List, Optional

from tooling.config.catalog import load_adapter
from tooling.config.composition import compose_bundle, load_manifest
from tooling.config.paths import ConfigError, prepare_output_root, resolve_beneath
from tooling.config.validate import validate


UNRESOLVED = re.compile(r"\{\{[^{}\n]+\}\}")


def canonical_bundle(root: Path, scope: str = "project") -> str:
    """Build the standalone minimal bundle used when no manifest is selected."""

    return compose_bundle(root, scope=scope)


def _reject_destination_symlinks(output_root: Path, destination: Path) -> None:
    relative = destination.relative_to(output_root)
    current = output_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ConfigError("render destination contains a symlink: {}".format(relative))


def _write_atomic(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=str(destination.parent),
            prefix=".ai-agent-config-",
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


def render(
    root: Path,
    adapter_id: str,
    output_root: Path,
    scope: str = "project",
    manifest_path: Optional[Path] = None,
    profile_path: Optional[Path] = None,
) -> List[Path]:
    """Render one validated adapter into caller-declared staging."""

    source_root = Path(root).resolve(strict=True)
    errors = validate(source_root)
    if errors:
        raise ConfigError("repository validation failed:\n{}".format("\n".join(errors)))

    adapter = load_adapter(source_root, adapter_id)
    if adapter.adapter_id != adapter_id:
        raise ConfigError("adapter id does not match requested adapter")
    manifest = None
    if manifest_path is not None:
        manifest = load_manifest(Path(manifest_path))
        if manifest["adapter"] != adapter_id:
            raise ConfigError(
                "manifest adapter '{}' does not match requested adapter '{}'".format(
                    manifest["adapter"], adapter_id
                )
            )

    template_path = resolve_beneath(
        source_root, adapter.template_path, must_exist=True, label="adapter template"
    )
    try:
        template = template_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ConfigError("cannot read adapter template: {}".format(error)) from error
    if template.count("{{CONTENT}}") != 1:
        raise ConfigError("adapter template must contain {{CONTENT}} exactly once")

    try:
        output_path = adapter.path_for(scope)
    except ValueError as error:
        raise ConfigError(str(error)) from error
    if manifest is not None:
        declared_output = manifest.get("output")
        if declared_output is not None and declared_output != output_path:
            raise ConfigError(
                "manifest output '{}' does not match adapter output '{}'".format(
                    declared_output, output_path
                )
            )
    bundle = compose_bundle(
        source_root,
        scope=scope,
        manifest_path=manifest_path,
        profile_path=profile_path,
    )
    rendered = template.replace("{{CONTENT}}", bundle.rstrip("\n"))
    unresolved = UNRESOLVED.search(rendered)
    if unresolved:
        raise ConfigError(
            "rendered output contains unresolved placeholder '{}'".format(
                unresolved.group(0)
            )
        )
    if not rendered.endswith("\n"):
        rendered += "\n"

    staging_root = prepare_output_root(source_root, output_root)
    destination = resolve_beneath(
        staging_root,
        output_path,
        must_exist=False,
        label="adapter output path",
    )
    _reject_destination_symlinks(staging_root, destination)
    _write_atomic(destination, rendered)
    return [destination]
