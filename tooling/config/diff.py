"""Read-only comparison between rendered policy and a supplied target."""

import difflib
import tempfile
from pathlib import Path

from tooling.config.catalog import load_adapter
from tooling.config.paths import ConfigError, resolve_beneath
from tooling.config.render import render


def diff(
    root: Path,
    adapter_id: str,
    target_root: Path,
    scope: str = "project",
) -> str:
    """Return a unified diff without creating or changing target files."""

    source_root = Path(root).resolve(strict=True)
    requested_target = Path(target_root)
    if requested_target.is_symlink():
        raise ConfigError("target root cannot be a symlink: {}".format(target_root))
    try:
        resolved_target = requested_target.resolve(strict=True)
    except FileNotFoundError as error:
        raise ConfigError("target root does not exist: {}".format(target_root)) from error
    if not resolved_target.is_dir():
        raise ConfigError("target root is not a directory: {}".format(target_root))

    adapter = load_adapter(source_root, adapter_id)
    try:
        output_path = adapter.path_for(scope)
    except ValueError as error:
        raise ConfigError(str(error)) from error
    target_path = resolve_beneath(
        resolved_target,
        output_path,
        must_exist=False,
        label="target path",
    )
    if target_path.exists() and not target_path.is_file():
        raise ConfigError("target path is not a regular file: {}".format(output_path))
    try:
        target_text = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
    except (OSError, UnicodeError) as error:
        raise ConfigError("cannot read target path: {}".format(error)) from error

    with tempfile.TemporaryDirectory(prefix="ai-agent-config-diff-") as directory:
        rendered_path = render(source_root, adapter_id, Path(directory), scope=scope)[0]
        rendered_text = rendered_path.read_text(encoding="utf-8")

    if target_text == rendered_text:
        return ""
    return "".join(
        difflib.unified_diff(
            target_text.splitlines(keepends=True),
            rendered_text.splitlines(keepends=True),
            fromfile="target/{}".format(output_path),
            tofile="rendered/{}".format(output_path),
        )
    )
