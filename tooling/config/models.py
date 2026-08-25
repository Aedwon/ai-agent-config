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
    official_sources: Tuple[Dict[str, str], ...]
    recognition: Dict[str, Any]
