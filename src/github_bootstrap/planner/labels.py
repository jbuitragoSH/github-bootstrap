from github_bootstrap.github.label_state import LabelState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import ProjectSpecification


def plan_labels(
    specification: ProjectSpecification,
    state: LabelState,
) -> list[PlanAction]:
    """Generate the actions required to synchronize repository labels."""

    actions: list[PlanAction] = []

    for label in specification.labels:
        if label.name not in state.labels:
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

    return actions
