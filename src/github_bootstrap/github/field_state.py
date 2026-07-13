"""GitHub Project field state."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldState:
    """Current GitHub Project fields."""

    fields: set[str]
