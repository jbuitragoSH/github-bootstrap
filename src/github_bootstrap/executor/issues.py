"""Execute GitHub issue actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.planner.actions import PlanAction

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


def execute_issue_action(
    client: GitHubClient,
    context: ExecutionContext,
    action: PlanAction,
) -> None:
    """Execute an issue action."""

    if action.operation != "create":
        return

    if context.project_id is None:
        raise ValueError("Project ID is required to add issues to the project.")

    issue = client.issues.create(
        owner=context.owner,
        repository=context.repository,
        title=action.payload["title"],
        body=action.payload.get("body"),
        labels=action.payload.get("labels"),
        milestone=action.payload.get("milestone"),
    )

    client.project_items.add(
        project_id=context.project_id,
        content_id=issue.id,
    )
