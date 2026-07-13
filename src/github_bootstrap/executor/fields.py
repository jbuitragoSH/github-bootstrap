"""Field action executor."""

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.planner.actions import PlanAction


def execute_field_action(
    client: GitHubClient,
    context: ExecutionContext,
    action: PlanAction,
) -> None:
    """Execute a field action."""

    if action.operation != "create":
        return

    if context.project_id is None:
        raise ValueError("Project ID is required to create fields.")

    client.fields.create(
        project_id=context.project_id,
        name=action.payload["name"],
        data_type=action.payload["data_type"],
    )
