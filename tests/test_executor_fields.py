from unittest.mock import MagicMock

import pytest

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.fields import execute_field_action
from github_bootstrap.planner.actions import PlanAction


def test_execute_text_field_create_action() -> None:
    client = MagicMock()
    client.fields = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repo-id",
        owner="org",
        repository="repo",
        project_id="project-id",
    )

    action = PlanAction(
        operation="create",
        resource="field",
        description="Create text field 'Component'",
        payload={
            "name": "Component",
            "data_type": "TEXT",
        },
    )

    execute_field_action(client, context, action)

    client.fields.create.assert_called_once_with(
        project_id="project-id",
        name="Component",
        data_type="TEXT",
        options=None,
    )


def test_execute_single_select_field_create_action() -> None:
    client = MagicMock()
    client.fields = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repo-id",
        owner="org",
        repository="repo",
        project_id="project-id",
    )

    action = PlanAction(
        operation="create",
        resource="field",
        description="Create single-select field 'Priority'",
        payload={
            "name": "Priority",
            "data_type": "SINGLE_SELECT",
            "options": ["Low", "Medium", "High"],
        },
    )

    execute_field_action(client, context, action)

    client.fields.create.assert_called_once_with(
        project_id="project-id",
        name="Priority",
        data_type="SINGLE_SELECT",
        options=["Low", "Medium", "High"],
    )


def test_execute_iteration_field_create_action() -> None:
    client = MagicMock()
    client.fields = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repo-id",
        owner="org",
        repository="repo",
        project_id="project-id",
    )

    action = PlanAction(
        operation="create",
        resource="field",
        description="Create iteration field 'Sprint'",
        payload={
            "name": "Sprint",
            "data_type": "ITERATION",
        },
    )

    execute_field_action(client, context, action)

    client.fields.create.assert_called_once_with(
        project_id="project-id",
        name="Sprint",
        data_type="ITERATION",
        options=None,
    )


def test_execute_field_action_skips_drift_actions() -> None:
    client = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
        project_id="project-id",
    )

    action = PlanAction(
        operation="drift",
        resource="field",
        description="Field 'Priority' exists with drift: options differ",
        payload={
            "name": "Priority",
            "reason": "options differ",
        },
    )

    execute_field_action(
        client,
        context,
        action,
    )

    client.fields.create.assert_not_called()


def test_execute_field_action_rejects_unknown_operations() -> None:
    client = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
        project_id="project-id",
    )

    action = PlanAction(
        operation="update",
        resource="field",
        description="Update field",
        payload={
            "name": "Priority",
        },
    )

    with pytest.raises(
        ValueError,
        match="Unsupported field action operation: update",
    ):
        execute_field_action(
            client,
            context,
            action,
        )
