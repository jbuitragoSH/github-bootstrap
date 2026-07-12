"""GitHub models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GitHubProject:
    """GitHub Project V2."""

    id: str
    title: str


@dataclass(frozen=True)
class GitHubRepository:
    """GitHub repository."""

    id: str
    name: str


@dataclass(frozen=True)
class GitHubLabel:
    """GitHub repository label."""

    id: str
    name: str
