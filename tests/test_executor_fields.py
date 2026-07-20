from datetime import date
from unittest.mock import MagicMock

import pytest

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.fields import execute_field_action
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import Iteration


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
        duration=None,
        start_date=None,
        iterations=None,
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
        duration=None,
        start_date=None,
        iterations=None,
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
            "duration": 14,
            "start_date": date(2026, 8, 1),
            "iterations": [
                Iteration(title="Sprint 1"),
                Iteration(title="Sprint 2"),
                Iteration(title="Sprint 3"),
            ],
        },
    )

    execute_field_action(client, context, action)

    client.fields.create.assert_called_once_with(
        project_id="project-id",
        name="Sprint",
        data_type="ITERATION",
        options=None,
        duration=14,
        start_date=date(2026, 8, 1),
        iterations=[
            Iteration(title="Sprint 1"),
            Iteration(title="Sprint 2"),
            Iteration(title="Sprint 3"),
        ],
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
