"""GitHub label state."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LabelSnapshot:
    """Current GitHub label configuration."""

    name: str
    color: str
    description: str | None = None


@dataclass(frozen=True)
class LabelState:
    """Current GitHub labels."""

    labels: dict[str, LabelSnapshot] = field(default_factory=dict)
