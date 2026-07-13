from unittest.mock import MagicMock

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.fields import execute_field_action
from github_bootstrap.planner.actions import PlanAction


def test_execute_field_create_action() -> None:
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
    )
