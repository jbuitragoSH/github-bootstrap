from datetime import date
from unittest.mock import MagicMock

import pytest

from github_bootstrap.github.client import GitHubClient
from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.milestone_state import MilestoneSnapshot
from github_bootstrap.github.milestones import MilestonesAPI


def test_client_exposes_milestones_api() -> None:
    client = GitHubClient(
        token="token",
    )

    assert isinstance(
        client.milestones,
        MilestonesAPI,
    )


def test_find_returns_open_repository_milestones() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "repository": {
            "milestones": {
                "nodes": [
                    {
                        "title": "Sprint 1",
                        "description": "Foundation capabilities",
                        "dueOn": "2026-07-31T00:00:00Z",
                    },
                    {
                        "title": "Sprint 2",
                        "description": "Advanced features",
                        "dueOn": "2026-08-31T00:00:00Z",
                    },
                ],
            },
        },
    }

    api = MilestonesAPI(client)

    state = api.find(
        owner="org",
        repository="repo",
    )

    assert set(state.milestones) == {
        "Sprint 1",
        "Sprint 2",
    }
    assert state.milestones["Sprint 1"] == MilestoneSnapshot(
        title="Sprint 1",
        description="Foundation capabilities",
        due_on=date(2026, 7, 31),
    )
    assert state.milestones["Sprint 2"] == MilestoneSnapshot(
        title="Sprint 2",
        description="Advanced features",
        due_on=date(2026, 8, 31),
    )

    client.execute.assert_called_once()

    _, variables = client.execute.call_args.args

    assert variables == {
        "owner": "org",
        "repository": "repo",
    }


def test_find_returns_empty_state_when_repository_has_no_milestones() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "repository": {
            "milestones": {
                "nodes": [],
            },
        },
    }

    api = MilestonesAPI(client)

    state = api.find(
        owner="org",
        repository="repo",
    )

    assert state.milestones == {}


def test_find_raises_error_for_invalid_repository_response() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "repository": None,
    }

    api = MilestonesAPI(client)

    with pytest.raises(
        GitHubError,
        match="Invalid response from GitHub API.",
    ):
        api.find(
            owner="org",
            repository="repo",
        )


def test_create_repository_milestone() -> None:
    client = MagicMock()

    client.execute_rest.return_value = {
        "node_id": "milestone-node-id",
        "number": 1,
        "title": "Sprint 1",
    }

    api = MilestonesAPI(client)

    milestone = api.create(
        owner="org",
        repository="repo",
        title="Sprint 1",
        description="Foundation capabilities",
        due_on=date(2026, 7, 31),
    )

    client.execute_rest.assert_called_once_with(
        "POST",
        "/repos/org/repo/milestones",
        {
            "title": "Sprint 1",
            "description": "Foundation capabilities",
            "due_on": "2026-07-31",
        },
    )

    assert milestone.id == "milestone-node-id"
    assert milestone.number == 1
    assert milestone.title == "Sprint 1"


def test_create_repository_milestone_without_optional_fields() -> None:
    client = MagicMock()

    client.execute_rest.return_value = {
        "node_id": "milestone-node-id",
        "number": 1,
        "title": "Sprint 1",
    }

    api = MilestonesAPI(client)

    api.create(
        owner="org",
        repository="repo",
        title="Sprint 1",
    )

    client.execute_rest.assert_called_once_with(
        "POST",
        "/repos/org/repo/milestones",
        {
            "title": "Sprint 1",
            "description": None,
            "due_on": None,
        },
    )
