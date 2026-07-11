"""Plan actions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanAction:
    """A synchronization action."""

    operation: str
    resource: str
    description: str
