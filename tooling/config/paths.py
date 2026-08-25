"""Path containment rules shared by every configuration command."""

from pathlib import Path, PurePosixPath


class ConfigError(ValueError):
    """A configuration request is unsafe or invalid."""


def _is_beneath(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def safe_relative_path(value: str, label: str = "path") -> PurePosixPath:
    """Return a normalized portable path or reject an unsafe value."""

    if not isinstance(value, str) or not value or "\x00" in value:
        raise ConfigError("{} must be a non-empty relative path".format(label))
    if "\\" in value:
        raise ConfigError("{} must use forward slashes".format(label))

    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ConfigError("{} must stay below its declared root".format(label))
    return path


def resolve_beneath(
    root: Path, relative: str, must_exist: bool = False, label: str = "path"
) -> Path:
    """Resolve a relative path without allowing a symlink escape."""

    root_path = Path(root)
    try:
        resolved_root = root_path.resolve(strict=True)
    except FileNotFoundError as error:
        raise ConfigError("declared root does not exist: {}".format(root_path)) from error
    if not resolved_root.is_dir():
        raise ConfigError("declared root is not a directory: {}".format(root_path))

    portable = safe_relative_path(relative, label)
    candidate = resolved_root.joinpath(*portable.parts)
    try:
        resolved_candidate = candidate.resolve(strict=must_exist)
    except FileNotFoundError as error:
        raise ConfigError("{} does not exist: {}".format(label, relative)) from error

    if not _is_beneath(resolved_candidate, resolved_root):
        raise ConfigError("{} escapes its declared root: {}".format(label, relative))
    if must_exist and not candidate.exists():
        raise ConfigError("{} does not exist: {}".format(label, relative))
    return candidate


def prepare_output_root(source_root: Path, output_root: Path) -> Path:
    """Create a plain staging directory outside the canonical source root."""

    try:
        resolved_source = Path(source_root).resolve(strict=True)
    except FileNotFoundError as error:
        raise ConfigError("source root does not exist: {}".format(source_root)) from error
    if not resolved_source.is_dir():
        raise ConfigError("source root is not a directory: {}".format(source_root))

    requested_output = Path(output_root)
    if requested_output.is_symlink():
        raise ConfigError("output root cannot be a symlink: {}".format(output_root))
    resolved_output = requested_output.resolve(strict=False)
    if resolved_output == resolved_source or _is_beneath(resolved_output, resolved_source):
        raise ConfigError("output root must be outside the source root")
    if resolved_output.exists() and not resolved_output.is_dir():
        raise ConfigError("output root is not a directory: {}".format(output_root))

    resolved_output.mkdir(parents=True, exist_ok=True)
    return resolved_output
