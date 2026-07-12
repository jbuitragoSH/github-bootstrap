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

    project = specification["project"]

    if not isinstance(project, dict):
        raise SpecificationValidationError("Field 'project' must be a mapping.")

    if "title" not in project:
        raise SpecificationValidationError("Missing required field: project.title")

    return specification
