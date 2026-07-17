"""GitHub milestone state."""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class MilestoneSnapshot:
    """Current GitHub milestone configuration."""

    title: str
    description: str | None = None
    due_on: date | None = None


@dataclass(frozen=True)
class MilestoneState:
    """Current GitHub milestones."""

    milestones: dict[str, MilestoneSnapshot] = field(default_factory=dict)
