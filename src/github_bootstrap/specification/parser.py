"""Parse validated specifications into domain models."""

from datetime import date
from typing import Any

from github_bootstrap.specification.models import (
    Label,
    Milestone,
    Project,
    ProjectSpecification,
)


def parse_specification(
    specification: dict[str, Any],
) -> ProjectSpecification:
    """Convert a validated specification into domain models."""

    return ProjectSpecification(
        organization=specification["organization"],
        repository=specification["repository"],
        project=_parse_project(specification),
        labels=_parse_labels(specification),
        milestones=_parse_milestones(specification),
    )


def _parse_project(
    specification: dict[str, Any],
) -> Project:
    """Parse project definition."""

    project = specification["project"]

    return Project(
        title=project["title"],
    )


def _parse_labels(
    specification: dict[str, Any],
) -> list[Label]:
    """Parse label definitions."""

    labels = specification.get("labels", [])

    return [
        Label(
            name=label["name"],
            color=label["color"],
            description=label.get("description"),
        )
        for label in labels
    ]


def _parse_milestones(
    specification: dict[str, Any],
) -> list[Milestone]:
    """Parse milestone definitions."""

    milestones = specification.get("milestones", [])

    return [
        Milestone(
            title=milestone["title"],
            description=milestone.get("description"),
            due_on=_parse_optional_date(milestone.get("due_on")),
        )
        for milestone in milestones
    ]


def _parse_optional_date(value: object) -> date | None:
    """Parse an optional ISO date value."""

    if value is None:
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    raise TypeError("Date value must be a date, ISO date string, or None.")
