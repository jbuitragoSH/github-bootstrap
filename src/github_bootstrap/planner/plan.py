"""Models for synchronization plans."""

from dataclasses import dataclass, field


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
