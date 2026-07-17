from unittest.mock import MagicMock

import pytest

from github_bootstrap.github.client import GitHubClient
from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.fields import FieldsAPI


def test_client_exposes_fields_api() -> None:
    client = GitHubClient(
        token="token",
    )

    assert isinstance(
        client.fields,
        FieldsAPI,
    )


def test_find_returns_project_fields() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "viewer": {
            "projectsV2": {
                "nodes": [
                    {
                        "title": "Other Project",
                        "fields": {
                            "nodes": [
                                {
                                    "name": "Other Field",
                                },
                            ],
                        },
                    },
                    {
                        "title": "Knowledge Platform",
                        "fields": {
                            "nodes": [
                                {
                                    "name": "Title",
                                },
                                {
                                    "name": "Status",
                                },
                                {
                                    "name": "Priority",
                                },
                            ],
                        },
                    },
                ],
            },
        },
    }

    api = FieldsAPI(client)

    state = api.find(
        project_title="Knowledge Platform",
    )

    assert state.fields == {
        "Title",
        "Status",
        "Priority",
    }

    client.execute.assert_called_once()


def test_find_returns_empty_state_when_project_has_no_fields() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "viewer": {
            "projectsV2": {
                "nodes": [
                    {
                        "title": "Knowledge Platform",
                        "fields": {
                            "nodes": [],
                        },
                    },
                ],
            },
        },
    }

    api = FieldsAPI(client)

    state = api.find(
        project_title="Knowledge Platform",
    )

    assert state.fields == set()


def test_find_returns_empty_state_when_project_does_not_exist() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "viewer": {
            "projectsV2": {
                "nodes": [],
            },
        },
    }

    api = FieldsAPI(client)

    state = api.find(
        project_title="Knowledge Platform",
    )

    assert state.fields == set()


def test_find_raises_error_for_invalid_viewer_response() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "viewer": None,
    }

    api = FieldsAPI(client)

    with pytest.raises(
        GitHubError,
        match="Invalid response from GitHub API.",
    ):
        api.find(
            project_title="Knowledge Platform",
        )


def test_create_single_select_field_calls_execute() -> None:
    client = MagicMock()

    api = FieldsAPI(client)

    api.create(
        project_id="project-id",
        name="Priority",
        data_type="SINGLE_SELECT",
        options=["Low", "Medium"],
    )

    client.execute.assert_called_once()

    args = client.execute.call_args[0]

    assert "SINGLE_SELECT" in args[0]
    assert args[1]["options"] == [
        {
            "name": "Low",
            "color": "GRAY",
            "description": "",
        },
        {
            "name": "Medium",
            "color": "GRAY",
            "description": "",
        },
    ]


def test_create_iteration_field_calls_execute() -> None:
    client = MagicMock()

    api = FieldsAPI(client)

    api.create(
        project_id="project-id",
        name="Sprint",
        data_type="ITERATION",
    )

    client.execute.assert_called_once()

    query, variables = client.execute.call_args[0]

    assert "ITERATION" in query
    assert "iterationConfiguration" in query

    assert variables["projectId"] == "project-id"
    assert variables["name"] == "Sprint"

    configuration = variables["configuration"]

    assert configuration["duration"] == 14
    assert isinstance(configuration["startDate"], str)
    assert configuration["iterations"] == []
