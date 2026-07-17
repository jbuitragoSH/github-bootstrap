"""Execute GitHub Project field actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.planner.actions import PlanAction

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


def execute_field_action(
    client: GitHubClient,
    context: ExecutionContext,
    action: PlanAction,
) -> None:
    """Execute a field synchronization action."""

    if action.operation == "drift":
        return

    if action.operation != "create":
        raise ValueError(f"Unsupported field action operation: {action.operation}")

    if context.project_id is None:
        raise ValueError("Project ID is required to create fields.")

    client.fields.create(
        project_id=context.project_id,
        name=action.payload["name"],
        data_type=action.payload["data_type"],
        options=action.payload.get("options"),
    )
