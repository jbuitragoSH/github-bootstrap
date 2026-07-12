"""Parse validated specifications into domain models."""

from typing import Any

from github_bootstrap.specification.models import (
    Label,
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
