"""GitHub Project item state."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProjectItemSnapshot:
    """Current GitHub Project item."""

    id: str
    content_id: str


@dataclass(frozen=True)
class ProjectItemState:
    """Current GitHub Project items."""

    items: dict[str, ProjectItemSnapshot] = field(default_factory=dict)
