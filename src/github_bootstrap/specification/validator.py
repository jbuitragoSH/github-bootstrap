"""Validate GitHub project specifications."""

from typing import Any


class SpecificationValidationError(Exception):
    """Raised when specification validation fails."""


def validate_specification(
    specification: dict[str, Any],
) -> dict[str, Any]:
    """Validate required specification fields.

    Args:
        specification: Parsed YAML specification.

    Raises:
        SpecificationValidationError: If invalid.
    """
    required_fields = [
        "organization",
        "repository",
        "project",
    ]

    for field in required_fields:
        if field not in specification:
            raise SpecificationValidationError(f"Missing required field: {field}")

    _validate_project(specification["project"])
    _validate_milestones(specification.get("milestones", []))

    return specification


def _validate_project(project: Any) -> None:
    """Validate project configuration."""

    if not isinstance(project, dict):
        raise SpecificationValidationError("Field 'project' must be a mapping.")

    if "title" not in project:
        raise SpecificationValidationError("Missing required field: project.title")


def _validate_milestones(milestones: Any) -> None:
    """Validate milestone configurations."""

    if not isinstance(milestones, list):
        raise SpecificationValidationError("Field 'milestones' must be a list.")

    for index, milestone in enumerate(milestones):
        if not isinstance(milestone, dict):
            raise SpecificationValidationError(
                f"Field 'milestones[{index}]' must be a mapping."
            )

        if "title" not in milestone:
            raise SpecificationValidationError(
                f"Missing required field: milestones[{index}].title"
            )
