"""Models for synchronization plans."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Plan:
    """Represents changes required to synchronize GitHub."""

    actions: list[str] = field(default_factory=list)

    def add(self, action: str) -> None:
        """Add an action to the plan."""
        self.actions.append(action)

    def is_empty(self) -> bool:
        """Return True when no actions exist."""
        return not self.actions


def create_plan(
    specification: dict[str, Any],
) -> Plan:
    """Create synchronization plan from specification."""
    plan = Plan()

    project = specification["project"]
    title = project["title"]

    plan.add(f"Create Project V2: {title}")

    return plan
