"""GitHub Project field state."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FieldOptionSnapshot:
    """Current GitHub single-select field option."""

    id: str
    name: str


@dataclass(frozen=True)
class IterationSnapshot:
    """Current GitHub iteration option."""

    id: str
    title: str


@dataclass(frozen=True)
class FieldSnapshot:
    """Current GitHub Project field configuration."""

    id: str
    name: str
    data_type: str
    options: tuple[FieldOptionSnapshot, ...] = ()
    iterations: tuple[IterationSnapshot, ...] = ()


@dataclass(frozen=True)
class FieldState:
    """Current GitHub Project fields."""

    fields: dict[str, FieldSnapshot] = field(default_factory=dict)
