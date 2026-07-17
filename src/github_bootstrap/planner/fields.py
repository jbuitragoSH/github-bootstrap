"""Plan GitHub Project field synchronization."""

from github_bootstrap.github.field_state import FieldState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import (
    DateField,
    Field,
    IterationField,
    NumberField,
    ProjectSpecification,
    SingleSelectField,
    TextField,
)


def plan_fields(
    specification: ProjectSpecification,
    state: FieldState,
) -> list[PlanAction]:
    """Generate actions required to synchronize GitHub Project fields."""

    actions: list[PlanAction] = []
    existing_fields = {_normalize(name) for name in state.fields}

    for field in specification.fields:
        if _normalize(field.name) in existing_fields:
            continue

        actions.append(
            _plan_create_field(field),
        )

    return actions


def _plan_create_field(
    project_field: Field,
) -> PlanAction:
    """Create a plan action for a field specification."""

    if isinstance(project_field, TextField):
        return _create_field_action(
            project_field,
            data_type="TEXT",
        )

    if isinstance(project_field, NumberField):
        return _create_field_action(
            project_field,
            data_type="NUMBER",
        )

    if isinstance(project_field, DateField):
        return _create_field_action(
            project_field,
            data_type="DATE",
        )

    if isinstance(project_field, SingleSelectField):
        return PlanAction(
            operation="create",
            resource="field",
            description=(f"Create single-select field '{project_field.name}'"),
            payload={
                "name": project_field.name,
                "data_type": "SINGLE_SELECT",
                "options": project_field.options,
            },
        )

    if isinstance(project_field, IterationField):
        return _create_field_action(
            project_field,
            data_type="ITERATION",
        )

    raise TypeError(f"Unsupported field specification: {type(project_field).__name__}")


def _create_field_action(
    project_field: Field,
    data_type: str,
) -> PlanAction:
    """Create a plan action for a field without additional configuration."""

    field_type = data_type.lower().replace("_", "-")

    return PlanAction(
        operation="create",
        resource="field",
        description=f"Create {field_type} field '{project_field.name}'",
        payload={
            "name": project_field.name,
            "data_type": data_type,
        },
    )


def _normalize(name: str) -> str:
    return name.strip().lower()
