"""GitHub Project field state."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FieldSnapshot:
    """Current GitHub Project field configuration."""

    name: str
    data_type: str
    options: tuple[str, ...] = ()


@dataclass(frozen=True)
class FieldState:
    """Current GitHub Project fields."""

    fields: dict[str, FieldSnapshot] = field(default_factory=dict)
