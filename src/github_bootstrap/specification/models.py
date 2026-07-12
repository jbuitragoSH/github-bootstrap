"""Specification models."""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Label:
    """GitHub label configuration."""

    name: str
    color: str
    description: str | None = None


@dataclass(frozen=True)
class Milestone:
    """GitHub milestone configuration."""

    title: str
    description: str | None = None
    due_on: date | None = None


@dataclass(frozen=True)
class Project:
    """GitHub Project configuration."""

    title: str


@dataclass(frozen=True)
class ProjectSpecification:
    """Root project specification."""

    organization: str
    repository: str
    project: Project
    labels: list[Label] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
