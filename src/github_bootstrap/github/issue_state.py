"""GitHub issue state."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class IssueSnapshot:
    """Current GitHub issue."""

    id: str
    number: int
    title: str


@dataclass(frozen=True)
class IssueState:
    """Current GitHub issues."""

    issues: dict[str, IssueSnapshot] = field(default_factory=dict)
