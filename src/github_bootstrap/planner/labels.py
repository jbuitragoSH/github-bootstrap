from github_bootstrap.github.label_state import LabelSnapshot, LabelState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import Label, ProjectSpecification


def plan_labels(
    specification: ProjectSpecification,
    state: LabelState,
) -> list[PlanAction]:
    actions: list[PlanAction] = []

    existing_labels = {
        _normalize(name): snapshot for name, snapshot in state.labels.items()
    }

    for label in specification.labels:
        snapshot = existing_labels.get(_normalize(label.name))

        if snapshot is None:
            actions.append(
                PlanAction(
                    operation="create",
                    resource="label",
                    description=f"Create label '{label.name}'",
                    payload={
                        "name": label.name,
                        "color": label.color,
                        "description": label.description,
                    },
                )
            )
            continue

        drift_reason = _detect_label_drift(label, snapshot)

        if drift_reason is not None:
            actions.append(
                PlanAction(
                    operation="drift",
                    resource="label",
                    description=(
                        f"Label '{label.name}' exists with drift: {drift_reason}"
                    ),
                    payload={
                        "name": label.name,
                        "reason": drift_reason,
                    },
                )
            )

    return actions


def _detect_label_drift(
    label: Label,
    snapshot: LabelSnapshot,
) -> str | None:
    if snapshot.color.lower() != label.color.lower():
        return "color differs"

    if _normalize_optional(snapshot.description) != _normalize_optional(
        label.description,
    ):
        return "description differs"

    return None


def _normalize(value: str) -> str:
    return value.strip().lower()


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()

    return normalized or None
