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
