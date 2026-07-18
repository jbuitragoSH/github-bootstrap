"""Execute GitHub issue actions."""

from __future__ import annotations

from datetime import date
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

    if context.project_id is None:
        raise ValueError(
            "Project ID is required to synchronize issues with the project."
        )

    if action.operation == "create":
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

        _configure_fields(
            client=client,
            context=context,
            item_id=item_id,
            issue_fields=action.payload.get("fields", {}),
        )

        return

    if action.operation == "sync_project_item":
        if context.project_id is None:
            raise ValueError("Project ID is required to synchronize issue fields.")

        project_item_id = action.payload.get("project_item_id")

        if isinstance(project_item_id, str):
            item_id = project_item_id
        else:
            issue_id = action.payload.get("issue_id")

            if not isinstance(issue_id, str):
                raise ValueError(
                    "Issue ID is required to add the issue to the project."
                )

            item_id = client.project_items.add(
                project_id=context.project_id,
                content_id=issue_id,
            )

        issue_fields = action.payload.get("fields", {})

        if not isinstance(issue_fields, dict):
            raise ValueError("Issue fields must be a dictionary.")

        _configure_fields(
            client,
            context,
            item_id,
            issue_fields,
        )

        return


def _configure_fields(
    client: GitHubClient,
    context: ExecutionContext,
    item_id: str,
    issue_fields: dict[str, object],
) -> None:
    """Configure Project V2 field values for an issue."""

    if not issue_fields:
        return

    if context.project_id is None:
        raise ValueError("Project ID is required to configure issue fields.")

    if context.field_state is None:
        raise ValueError("Field state is required to configure issue fields.")

    for field_name, value in issue_fields.items():
        field_snapshot = context.field_state.fields.get(field_name)

        if field_snapshot is None:
            continue

        if field_snapshot.data_type == "SINGLE_SELECT":
            if not isinstance(value, str):
                continue

            option_snapshot = next(
                (option for option in field_snapshot.options if option.name == value),
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

            continue

        if field_snapshot.data_type == "TEXT":
            if not isinstance(value, str):
                continue

            client.project_items.set_text_field(
                project_id=context.project_id,
                item_id=item_id,
                field_id=field_snapshot.id,
                value=value,
            )

            continue

        if field_snapshot.data_type == "NUMBER":
            if not isinstance(value, int | float):
                continue

            client.project_items.set_number_field(
                project_id=context.project_id,
                item_id=item_id,
                field_id=field_snapshot.id,
                value=value,
            )

            continue

        if field_snapshot.data_type == "DATE":
            if isinstance(value, date):
                date_value = value.isoformat()
            elif isinstance(value, str):
                date_value = value
            else:
                continue

            client.project_items.set_date_field(
                project_id=context.project_id,
                item_id=item_id,
                field_id=field_snapshot.id,
                value=date_value,
            )

            continue

        if field_snapshot.data_type == "ITERATION":
            if not isinstance(value, str):
                continue

            iteration_snapshot = next(
                (
                    iteration
                    for iteration in field_snapshot.iterations
                    if iteration.title == value
                ),
                None,
            )

            if iteration_snapshot is None:
                continue

            client.project_items.set_iteration_field(
                project_id=context.project_id,
                item_id=item_id,
                field_id=field_snapshot.id,
                iteration_id=iteration_snapshot.id,
            )
