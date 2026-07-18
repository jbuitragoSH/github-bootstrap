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

    item_id = client.project_items.add(
        project_id=context.project_id,
        content_id=issue.id,
    )

    issue_fields = action.payload.get("fields", {})

    if not issue_fields:
        return

    if context.field_state is None:
        raise ValueError("Field state is required to configure issue fields.")

    for field_name, option_name in issue_fields.items():
        field_snapshot = context.field_state.fields.get(field_name)

        if field_snapshot is None:
            continue

        if field_snapshot.data_type != "SINGLE_SELECT":
            continue

        option_snapshot = next(
            (option for option in field_snapshot.options if option.name == option_name),
            None,
        )

        if option_snapshot is None:
            continue

        client.project_items.set_single_select_field(
            project_id=context.project_id,
            item_id=item_id,
            field_id=field_snapshot.id,
            option_id=option_snapshot.id,
        )
