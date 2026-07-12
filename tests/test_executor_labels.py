from unittest.mock import MagicMock

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.labels import execute_label_action
from github_bootstrap.planner.actions import PlanAction


def test_execute_label_create_action() -> None:
    client = MagicMock()
    client.labels = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
    )

    action = PlanAction(
        operation="create",
        resource="label",
        description="Create label 'documentation'",
        payload={
            "name": "documentation",
            "color": "0075ca",
            "description": "Documentation improvements",
        },
    )

    execute_label_action(
        client,
        context,
        action,
    )

    client.labels.create.assert_called_once_with(
        repository_id="repository-id",
        name="documentation",
        color="0075ca",
        description="Documentation improvements",
    )


def test_execute_label_action_ignores_unsupported_operation() -> None:
    client = MagicMock()
    client.labels = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
    )

    action = PlanAction(
        operation="update",
        resource="label",
        description="Update label 'documentation'",
        payload={
            "name": "documentation",
            "color": "0075ca",
            "description": "Documentation improvements",
        },
    )

    execute_label_action(
        client,
        context,
        action,
    )

    client.labels.create.assert_not_called()
