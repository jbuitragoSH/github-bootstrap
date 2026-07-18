"""Models for synchronization plans."""

from dataclasses import dataclass, field

from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.planner.fields import plan_fields
from github_bootstrap.planner.issues import plan_issues
from github_bootstrap.planner.labels import plan_labels
from github_bootstrap.planner.milestones import plan_milestones
from github_bootstrap.planner.projects import plan_projects
from github_bootstrap.specification.models import ProjectSpecification


@dataclass
class Plan:
    """A synchronization plan."""

    actions: list[PlanAction] = field(default_factory=list)

    def add(
        self,
        action: PlanAction,
    ) -> None:
        """Add an action to the plan."""

        self.actions.append(action)

    def extend(
        self,
        actions: list[PlanAction],
    ) -> None:
        """Add multiple actions to the plan."""

        self.actions.extend(actions)

    def is_empty(self) -> bool:
        """Return whether the plan has no actions."""

        return len(self.actions) == 0

    def drift_actions(self) -> list[PlanAction]:
        """Return all detected drift actions."""

        return [action for action in self.actions if action.operation == "drift"]

    def executable_actions(self) -> list[PlanAction]:
        """Return actions that should be executed."""

        return [action for action in self.actions if action.operation != "drift"]

    def has_drift(self) -> bool:
        """Return whether the plan contains drift."""

        return len(self.drift_actions()) > 0


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

    plan.extend(
        plan_fields(
            specification,
            state.fields,
        )
    )

    plan.extend(
        plan_issues(
            specification,
            state.issues,
            state.milestones,
        )
    )

    return plan
