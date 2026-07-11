"""Models for synchronization plans."""

from dataclasses import dataclass, field

from github_bootstrap.github.state import ProjectState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import ProjectSpecification


@dataclass
class Plan:
    """Represents changes required to synchronize GitHub."""

    actions: list[PlanAction] = field(default_factory=list)

    def add(
        self,
        operation: str,
        resource: str,
        description: str,
    ) -> None:
        self.actions.append(
            PlanAction(
                operation=operation,
                resource=resource,
                description=description,
            )
        )

    def is_empty(self) -> bool:
        """Return True when no actions exist."""
        return not self.actions


def create_plan(
    specification: ProjectSpecification,
    state: ProjectState,
) -> Plan:
    """Create synchronization plan."""

    plan = Plan()

    title = specification.project.title

    if not state.exists:
        plan.add(
            operation="create",
            resource="project",
            description=f"Create Project V2: {title}",
        )

    return plan
