"""Parse validated specifications into domain models."""

from datetime import date
from typing import Any

from github_bootstrap.specification.models import (
    DateField,
    Field,
    Issue,
    IterationField,
    Label,
    Milestone,
    NumberField,
    Project,
    ProjectSpecification,
    SingleSelectField,
    TextField,
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
        fields=_parse_fields(specification),
        issues=[
            Issue(
                title=issue["title"],
                body=issue.get("body"),
                labels=issue.get("labels", []),
                milestone=issue.get("milestone"),
                fields=issue.get("fields", {}),
            )
            for issue in specification.get("issues", [])
        ],
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


def _parse_fields(
    specification: dict[str, Any],
) -> list[Field]:
    """Parse project field definitions."""

    fields = specification.get("fields", [])

    return [_parse_field(project_field) for project_field in fields]


def _parse_field(
    project_field: dict[str, Any],
) -> Field:
    """Parse a project field according to its type."""

    field_type = project_field["type"]
    name = project_field["name"]

    if field_type == "text":
        return TextField(name=name)

    if field_type == "number":
        return NumberField(name=name)

    if field_type == "date":
        return DateField(name=name)

    if field_type == "single_select":
        return SingleSelectField(
            name=name,
            options=project_field.get("options", []),
        )

    if field_type == "iteration":
        return IterationField(name=name)

    raise ValueError(f"Unsupported field type: {field_type}")


def _parse_optional_date(value: object) -> date | None:
    """Parse an optional ISO date value."""

    if value is None:
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    raise TypeError("Date value must be a date, ISO date string, or None.")
