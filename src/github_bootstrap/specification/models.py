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
class Field:
    """Base GitHub Project field configuration."""

    name: str


@dataclass(frozen=True)
class TextField(Field):
    """GitHub Project text field configuration."""


@dataclass(frozen=True)
class NumberField(Field):
    """GitHub Project number field configuration."""


@dataclass(frozen=True)
class DateField(Field):
    """GitHub Project date field configuration."""


@dataclass(frozen=True)
class SingleSelectField(Field):
    """GitHub Project single-select field configuration."""

    options: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IterationField(Field):
    """GitHub Project iteration field configuration."""


@dataclass(frozen=True)
class Project:
    """GitHub Project configuration."""

    title: str


@dataclass(frozen=True)
class Issue:
    """GitHub issue configuration."""

    title: str
    body: str | None = None
    labels: list[str] = field(default_factory=list)
    milestone: str | None = None
    fields: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectSpecification:
    """Root project specification."""

    organization: str
    repository: str
    project: Project
    labels: list[Label] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    fields: list[Field] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
