from dataclasses import dataclass


@dataclass(frozen=True)
class LabelState:
    """Repository labels."""

    labels: set[str]
