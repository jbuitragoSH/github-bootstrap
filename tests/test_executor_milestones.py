from datetime import date
from unittest.mock import MagicMock

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.milestones import execute_milestone_action
from github_bootstrap.planner.actions import PlanAction


def test_execute_milestone_create_action() -> None:
    client = MagicMock()
    client.milestones = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
    )

    action = PlanAction(
        operation="create",
        resource="milestone",
        description="Create milestone 'Sprint 1'",
        payload={
            "title": "Sprint 1",
            "description": "Foundation capabilities",
            "due_on": date(2026, 7, 31),
        },
    )

    execute_milestone_action(
        client,
        context,
        action,
    )

    client.milestones.create.assert_called_once_with(
        owner="org",
        repository="repo",
        title="Sprint 1",
        description="Foundation capabilities",
        due_on=date(2026, 7, 31),
    )


def test_execute_milestone_action_ignores_unsupported_operation() -> None:
    client = MagicMock()
    client.milestones = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
    )

    action = PlanAction(
        operation="update",
        resource="milestone",
        description="Update milestone 'Sprint 1'",
        payload={
            "title": "Sprint 1",
            "description": "Foundation capabilities",
            "due_on": None,
        },
    )

    execute_milestone_action(
        client,
        context,
        action,
    )

    client.milestones.create.assert_not_called()
