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

    client.issues.create(
        owner=context.owner,
        repository=context.repository,
        title=action.payload["title"],
        body=action.payload.get("body"),
        labels=action.payload.get("labels"),
        milestone=action.payload.get("milestone"),
    )
