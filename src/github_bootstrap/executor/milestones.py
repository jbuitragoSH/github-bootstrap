"""Milestone action executor."""

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.planner.actions import PlanAction


def execute_milestone_action(
    client: GitHubClient,
    context: ExecutionContext,
    action: PlanAction,
) -> None:
    """Execute a milestone action."""

    if action.operation != "create":
        return

    client.milestones.create(
        owner=context.owner,
        repository=context.repository,
        title=action.payload["title"],
        description=action.payload["description"],
        due_on=action.payload["due_on"],
    )
