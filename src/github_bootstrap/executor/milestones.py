"""Execute GitHub milestone actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.planner.actions import PlanAction

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


def execute_milestone_action(
    client: GitHubClient,
    context: ExecutionContext,
    action: PlanAction,
) -> None:
    """Execute a milestone synchronization action."""

    if action.operation == "drift":
        return

    if action.operation != "create":
        raise ValueError(f"Unsupported milestone action operation: {action.operation}")

    client.milestones.create(
        owner=context.owner,
        repository=context.repository,
        title=action.payload["title"],
        description=action.payload.get("description"),
        due_on=action.payload.get("due_on"),
    )
