"""Project action executor."""

from github_bootstrap.github.client import GitHubClient
from github_bootstrap.planner.actions import PlanAction


def execute_project_action(
    client: GitHubClient,
    owner_id: str,
    action: PlanAction,
) -> None:
    """Execute a project action."""

    if action.operation != "create":
        return

    client.projects.create(
        owner_id=owner_id,
        title=action.payload["title"],
    )
