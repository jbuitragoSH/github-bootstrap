from unittest.mock import MagicMock

import pytest

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.issues import execute_issue_action
from github_bootstrap.github.issue_state import IssueSnapshot
from github_bootstrap.planner.actions import PlanAction


def test_execute_issue_action_creates_issue_and_adds_it_to_project() -> None:
    client = MagicMock()

    client.issues.create.return_value = IssueSnapshot(
        id="issue-node-id",
        number=42,
        title="Implement academic program aggregate",
    )

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
        project_id="project-id",
    )

    action = PlanAction(
        operation="create",
        resource="issue",
        description="Create issue 'Implement academic program aggregate'",
        payload={
            "title": "Implement academic program aggregate",
            "body": "Implement the initial Academic Program aggregate.",
            "labels": ["domain"],
            "milestone": 1,
        },
    )

    execute_issue_action(
        client,
        context,
        action,
    )

    client.issues.create.assert_called_once_with(
        owner="org",
        repository="repo",
        title="Implement academic program aggregate",
        body="Implement the initial Academic Program aggregate.",
        labels=["domain"],
        milestone=1,
    )

    client.project_items.add.assert_called_once_with(
        project_id="project-id",
        content_id="issue-node-id",
    )


def test_execute_issue_action_requires_project_id() -> None:
    client = MagicMock()

    context = ExecutionContext(
        owner_id="owner-id",
        repository_id="repository-id",
        owner="org",
        repository="repo",
        project_id=None,
    )

    action = PlanAction(
        operation="create",
        resource="issue",
        description="Create issue 'Implement academic program aggregate'",
        payload={
            "title": "Implement academic program aggregate",
            "body": None,
            "labels": [],
            "milestone": None,
        },
    )

    with pytest.raises(
        ValueError,
        match="Project ID is required to synchronize issues with the project.",
    ):
        execute_issue_action(
            client,
            context,
            action,
        )

    client.issues.create.assert_not_called()
    client.project_items.add.assert_not_called()


def test_execute_issue_action_ignores_unsupported_operations() -> None:
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
        resource="issue",
        description="Update issue",
        payload={
            "title": "Implement academic program aggregate",
        },
    )

    execute_issue_action(
        client,
        context,
        action,
    )

    client.issues.create.assert_not_called()
    client.project_items.add.assert_not_called()
