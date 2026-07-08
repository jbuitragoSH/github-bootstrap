"""Load GitHub project specifications from YAML."""

from pathlib import Path
from typing import Any

import yaml


class SpecificationError(Exception):
    """Raised when the specification is invalid."""


def load_specification(path: Path) -> dict[str, Any]:
    """Load a YAML specification file.

    Args:
        path: Path to the YAML specification.

    Returns:
        Parsed YAML content.

    Raises:
        SpecificationError: If the file cannot be loaded.
    """
    if not path.exists():
        raise SpecificationError(f"Specification not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    if not isinstance(content, dict):
        raise SpecificationError("Specification root must be a YAML mapping.")

    return content
