"""Plan actions."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PlanAction:
    """A synchronization action."""

    operation: str
    resource: str
    description: str
    payload: dict[str, Any]
