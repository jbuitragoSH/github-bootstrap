"""Plan GitHub milestone synchronization."""

from github_bootstrap.github.milestone_state import (
    MilestoneSnapshot,
    MilestoneState,
)
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import (
    Milestone,
    ProjectSpecification,
)


def plan_milestones(
    specification: ProjectSpecification,
    state: MilestoneState,
) -> list[PlanAction]:
    """Generate actions required to synchronize GitHub milestones."""

    actions: list[PlanAction] = []

    existing_milestones = {
        _normalize(title): snapshot for title, snapshot in state.milestones.items()
    }

    for milestone in specification.milestones:
        snapshot = existing_milestones.get(
            _normalize(milestone.title),
        )

        if snapshot is None:
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
            continue

        drift_reason = _detect_milestone_drift(
            milestone,
            snapshot,
        )

        if drift_reason is not None:
            actions.append(
                PlanAction(
                    operation="drift",
                    resource="milestone",
                    description=(
                        f"Milestone '{milestone.title}' exists with drift: "
                        f"{drift_reason}"
                    ),
                    payload={
                        "title": milestone.title,
                        "reason": drift_reason,
                    },
                )
            )

    return actions


def _detect_milestone_drift(
    milestone: Milestone,
    snapshot: MilestoneSnapshot,
) -> str | None:
    """Detect drift between specification and current GitHub milestone."""

    if _normalize_optional(snapshot.description) != _normalize_optional(
        milestone.description,
    ):
        return "description differs"

    if snapshot.due_on != milestone.due_on:
        return "due date differs"

    return None


def _normalize(
    value: str,
) -> str:
    """Normalize values for case-insensitive comparisons."""

    return value.strip().lower()


def _normalize_optional(
    value: str | None,
) -> str | None:
    """Normalize optional strings."""

    if value is None:
        return None

    normalized = value.strip()

    if normalized == "":
        return None

    return normalized
