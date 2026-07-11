"""GitHub models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GitHubProject:
    """GitHub Project V2."""

    id: str
    title: str
