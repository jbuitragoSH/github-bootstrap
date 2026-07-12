"""Models for synchronization plans."""

from dataclasses import dataclass, field

from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.planner.labels import plan_labels
from github_bootstrap.planner.milestones import plan_milestones
from github_bootstrap.planner.projects import plan_projects
from github_bootstrap.specification.models import ProjectSpecification


@dataclass
class Plan:
    """Represents changes required to synchronize GitHub."""

    actions: list[PlanAction] = field(default_factory=list)

    def add(self, action: PlanAction) -> None:
        self.actions.append(action)

    def extend(self, actions: list[PlanAction]) -> None:
        self.actions.extend(actions)

    def is_empty(self) -> bool:
        return not self.actions


def create_plan(
    specification: ProjectSpecification,
    state: GitHubState,
) -> Plan:
    """Create a synchronization plan."""

    plan = Plan()

    plan.extend(
        plan_projects(
            specification,
            state.project,
        )
    )

    plan.extend(
        plan_labels(
            specification,
            state.labels,
        )
    )

    plan.extend(
        plan_milestones(
            specification,
            state.milestones,
        )
    )

    return plan
