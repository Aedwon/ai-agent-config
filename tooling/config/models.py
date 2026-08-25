"""Typed configuration records used by render and diff."""

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class Adapter:
    """A validated adapter record."""

    adapter_id: str
    label: str
    discovery_kind: str
    discovery_path: str
    template_path: str
    output_path: str
    output_category: str
    global_discovery_kind: str
    global_discovery_path: str
    global_output_path: str
    global_output_category: str
    global_official_sources: Tuple[Dict[str, str], ...]
    official_sources: Tuple[Dict[str, str], ...]
    recognition: Dict[str, Any]

    def path_for(self, scope: str) -> str:
        if scope == "project":
            return self.output_path
        if scope == "global":
            return self.global_output_path
        raise ValueError("scope must be project or global")
