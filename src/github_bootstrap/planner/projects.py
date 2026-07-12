"""Project synchronization planner."""

from github_bootstrap.github.state import ProjectState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import ProjectSpecification


def plan_projects(
    specification: ProjectSpecification,
    state: ProjectState,
) -> list[PlanAction]:
    """Generate the actions required to synchronize GitHub Projects."""

    actions: list[PlanAction] = []

    title = specification.project.title

    if not state.exists:
        actions.append(
            PlanAction(
                operation="create",
                resource="project",
                description=f"Create Project V2: {title}",
                payload={
                    "title": title,
                },
            )
        )

    return actions
