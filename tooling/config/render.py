"""Deterministic rendering into an explicit staging root."""

import os
import re
import tempfile
from pathlib import Path
from typing import List

from tooling.config.catalog import load_adapter
from tooling.config.paths import ConfigError, prepare_output_root, resolve_beneath
from tooling.config.validate import validate


CANONICAL_SOURCES = (
    "core/precedence.md",
    "core/agent-contract.md",
    "templates/minimal/AGENT_RULES.md",
)
UNRESOLVED = re.compile(r"\{\{[^{}\n]+\}\}")


def _markdown_body(text: str) -> str:
    if not text.startswith("---\n"):
        return text.strip()
    closing = text.find("\n---\n", 4)
    if closing == -1:
        raise ConfigError("canonical Markdown has unterminated frontmatter")
    return text[closing + 5 :].strip()


def canonical_bundle(root: Path) -> str:
    """Build the minimal canonical policy bundle in fixed order."""

    sections = []
    for relative in CANONICAL_SOURCES:
        path = resolve_beneath(root, relative, must_exist=True, label=relative)
        try:
            sections.append(_markdown_body(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError) as error:
            raise ConfigError("cannot read canonical source {}: {}".format(relative, error)) from error
    return "\n\n---\n\n".join(sections) + "\n"


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


def render(root: Path, adapter_id: str, output_root: Path) -> List[Path]:
    """Render one validated adapter into caller-declared staging."""

    source_root = Path(root).resolve(strict=True)
    errors = validate(source_root)
    if errors:
        raise ConfigError("repository validation failed:\n{}".format("\n".join(errors)))

    adapter = load_adapter(source_root, adapter_id)
    if adapter.adapter_id != adapter_id:
        raise ConfigError("adapter id does not match requested adapter")
    template_path = resolve_beneath(
        source_root, adapter.template_path, must_exist=True, label="adapter template"
    )
    try:
        template = template_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ConfigError("cannot read adapter template: {}".format(error)) from error
    if template.count("{{CONTENT}}") != 1:
        raise ConfigError("adapter template must contain {{CONTENT}} exactly once")

    rendered = template.replace("{{CONTENT}}", canonical_bundle(source_root).rstrip("\n"))
    unresolved = UNRESOLVED.search(rendered)
    if unresolved:
        raise ConfigError("rendered output contains unresolved placeholder '{}'".format(unresolved.group(0)))
    if not rendered.endswith("\n"):
        rendered += "\n"

    staging_root = prepare_output_root(source_root, output_root)
    destination = resolve_beneath(
        staging_root,
        adapter.output_path,
        must_exist=False,
        label="adapter output path",
    )
    _reject_destination_symlinks(staging_root, destination)
    _write_atomic(destination, rendered)
    return [destination]
