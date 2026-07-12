"""Plan repository milestone synchronization."""

from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import ProjectSpecification


def plan_milestones(
    specification: ProjectSpecification,
    state: MilestoneState,
) -> list[PlanAction]:
    """Generate actions required to synchronize repository milestones."""

    actions: list[PlanAction] = []

    for milestone in specification.milestones:
        if milestone.title not in state.milestones:
            actions.append(
                PlanAction(
                    operation="create",
                    resource="milestone",
                    description=f"Create milestone '{milestone.title}'",
                    payload={
                        "title": milestone.title,
                        "description": milestone.description,
                        "due_on": milestone.due_on,
                    },
                )
            )

    return actions
