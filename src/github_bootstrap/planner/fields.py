"""Plan GitHub Project field synchronization."""

from github_bootstrap.github.field_state import FieldSnapshot, FieldState
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

    existing_fields = {
        _normalize(name): snapshot for name, snapshot in state.fields.items()
    }

    for project_field in specification.fields:
        snapshot = existing_fields.get(_normalize(project_field.name))

        if snapshot is None:
            actions.append(
                _plan_create_field(project_field),
            )
            continue

        drift_reason = _detect_field_drift(
            project_field,
            snapshot,
        )

        if drift_reason is not None:
            actions.append(
                PlanAction(
                    operation="drift",
                    resource="field",
                    description=(
                        f"Field '{project_field.name}' exists with drift: "
                        f"{drift_reason}"
                    ),
                    payload={
                        "name": project_field.name,
                        "reason": drift_reason,
                    },
                )
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
        return PlanAction(
            operation="create",
            resource="field",
            description=(f"Create iteration field '{project_field.name}'"),
            payload={
                "name": project_field.name,
                "data_type": "ITERATION",
                "duration": project_field.duration,
                "start_date": project_field.start_date,
                "iterations": project_field.iterations,
            },
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


def _detect_field_drift(
    project_field: Field,
    snapshot: FieldSnapshot,
) -> str | None:
    """Detect drift between specification and current GitHub field."""

    expected_type = _expected_data_type(project_field)

    if snapshot.data_type != expected_type:
        return "type differs"

    if isinstance(project_field, SingleSelectField):
        expected_options = tuple(_normalize(option) for option in project_field.options)
        actual_options = tuple(_normalize(option.name) for option in snapshot.options)
        if actual_options != expected_options:
            return "options differ"

    return None


def _expected_data_type(
    project_field: Field,
) -> str:
    """Return the expected GitHub field data type."""

    if isinstance(project_field, TextField):
        return "TEXT"

    if isinstance(project_field, NumberField):
        return "NUMBER"

    if isinstance(project_field, DateField):
        return "DATE"

    if isinstance(project_field, SingleSelectField):
        return "SINGLE_SELECT"

    if isinstance(project_field, IterationField):
        return "ITERATION"

    raise TypeError(f"Unsupported field specification: {type(project_field).__name__}")


def _normalize(name: str) -> str:
    """Normalize field names for case-insensitive comparisons."""

    return name.strip().lower()
