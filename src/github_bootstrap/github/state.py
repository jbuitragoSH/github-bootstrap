"""GitHub current state models."""

from dataclasses import dataclass


@dataclass
class ProjectState:
    """Current GitHub project state."""

    exists: bool
    title: str | None = None
