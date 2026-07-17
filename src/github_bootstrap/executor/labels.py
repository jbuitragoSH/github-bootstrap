"""Label action executor."""

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.planner.actions import PlanAction


def execute_label_action(
    client: GitHubClient,
    context: ExecutionContext,
    action: PlanAction,
) -> None:
    """Execute a label action."""

    if action.operation == "drift":
        return

    if action.operation != "create":
        raise ValueError(f"Unsupported label action operation: {action.operation}")

    client.labels.create(
        repository_id=context.repository_id,
        name=action.payload["name"],
        color=action.payload["color"],
        description=action.payload["description"],
    )
