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
    _validate_fields(specification.get("fields", []))

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


def _validate_fields(fields: Any) -> None:
    """Validate project field configurations."""

    if not isinstance(fields, list):
        raise SpecificationValidationError("Field 'fields' must be a list.")

    supported_types = {
        "text",
        "number",
        "date",
        "single_select",
        "iteration",
    }

    for index, project_field in enumerate(fields):
        if not isinstance(project_field, dict):
            raise SpecificationValidationError(
                f"Field 'fields[{index}]' must be a mapping."
            )

        if "name" not in project_field:
            raise SpecificationValidationError(
                f"Missing required field: fields[{index}].name"
            )

        if "type" not in project_field:
            raise SpecificationValidationError(
                f"Missing required field: fields[{index}].type"
            )

        field_type = project_field["type"]

        if field_type not in supported_types:
            raise SpecificationValidationError(
                f"Unsupported field type: fields[{index}].type={field_type!r}"
            )

        if field_type == "single_select":
            _validate_single_select_options(
                project_field.get("options", []),
                index,
            )


def _validate_single_select_options(
    options: Any,
    field_index: int,
) -> None:
    """Validate single-select field options."""

    if not isinstance(options, list):
        raise SpecificationValidationError(
            f"Field 'fields[{field_index}].options' must be a list."
        )

    for option_index, option in enumerate(options):
        if not isinstance(option, str):
            raise SpecificationValidationError(
                "Field "
                f"'fields[{field_index}].options[{option_index}]' "
                "must be a string."
            )
