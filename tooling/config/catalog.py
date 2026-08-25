"""Load constrained repository catalogs after path validation."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from tooling.config.models import Adapter
from tooling.config.paths import ConfigError, resolve_beneath


ADAPTER_ID = re.compile(r"^[a-z][a-z0-9-]*$")


def load_json_file(root: Path, relative: str) -> Dict[str, Any]:
    path = resolve_beneath(root, relative, must_exist=True, label=relative)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConfigError("{} is not valid UTF-8 JSON: {}".format(relative, error)) from error
    if not isinstance(value, dict):
        raise ConfigError("{} must contain a JSON object".format(relative))
    return value


def list_adapter_ids(root: Path) -> List[str]:
    adapters_root = resolve_beneath(root, "adapters", must_exist=True, label="adapters")
    return sorted(
        path.parent.name
        for path in adapters_root.glob("*/adapter.json")
        if path.is_file() and not path.is_symlink()
    )


def load_adapter(root: Path, adapter_id: str) -> Adapter:
    if not ADAPTER_ID.fullmatch(adapter_id):
        raise ConfigError("invalid adapter id: {}".format(adapter_id))
    relative = "adapters/{}/adapter.json".format(adapter_id)
    data = load_json_file(root, relative)
    try:
        discovery = data["discovery"]
        template = data["template"]
        output = data["output"]
        global_target = data["global"]
        global_discovery = global_target["discovery"]
        global_output = global_target["output"]
        sources = tuple(discovery["official_sources"])
        return Adapter(
            adapter_id=data["id"],
            label=data["label"],
            discovery_kind=discovery["kind"],
            discovery_path=discovery["project_path"],
            template_path=template["path"],
            output_path=output["path"],
            output_category=output["category"],
            global_discovery_kind=global_discovery["kind"],
            global_discovery_path=global_discovery["path"],
            global_output_path=global_output["path"],
            global_output_category=global_output["category"],
            global_official_sources=tuple(global_discovery["official_sources"]),
            official_sources=sources,
            recognition=dict(data["recognition"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ConfigError("{} is incomplete: {}".format(relative, error)) from error


def load_skill_catalog(root: Path) -> Dict[str, Any]:
    return load_json_file(root, "skills/catalog.yaml")
