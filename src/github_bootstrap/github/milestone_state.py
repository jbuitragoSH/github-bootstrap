"""GitHub milestone state."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MilestoneState:
    """Repository milestones."""

    milestones: set[str]
