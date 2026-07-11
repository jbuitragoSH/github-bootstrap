"""Tests for the GitHub GraphQL client."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from github_bootstrap.github.client import GitHubClient
from github_bootstrap.github.exceptions import GitHubError


def make_response(
    status_code: int,
    payload: dict[str, Any],
) -> Mock:
    """Create a mocked HTTP response."""

    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


@patch("github_bootstrap.github.client.httpx.post")
def test_execute_returns_data(mock_post: Mock) -> None:
    """execute() returns GraphQL data."""

    mock_post.return_value = make_response(
        200,
        {
            "data": {
                "viewer": {
                    "login": "octocat",
                }
            }
        },
    )

    client = GitHubClient(token="token")

    data = client.execute("query {}")

    assert data["viewer"]["login"] == "octocat"


@patch("github_bootstrap.github.client.httpx.post")
def test_execute_http_error(mock_post: Mock) -> None:
    """HTTP errors raise GitHubError."""

    mock_post.return_value = make_response(
        500,
        {},
    )

    client = GitHubClient(token="token")

    with pytest.raises(GitHubError):
        client.execute("query {}")


@patch("github_bootstrap.github.client.httpx.post")
def test_execute_graphql_error(mock_post: Mock) -> None:
    """GraphQL errors raise GitHubError."""

    mock_post.return_value = make_response(
        200,
        {
            "errors": [
                {
                    "message": "Boom",
                }
            ]
        },
    )

    client = GitHubClient(token="token")

    with pytest.raises(GitHubError):
        client.execute("query {}")


@patch("github_bootstrap.github.client.httpx.post")
def test_viewer_returns_user(mock_post: Mock) -> None:
    """viewer() returns authenticated user."""

    mock_post.return_value = make_response(
        200,
        {
            "data": {
                "viewer": {
                    "id": "123",
                    "login": "octocat",
                }
            }
        },
    )

    client = GitHubClient(token="token")

    viewer = client.viewer()

    assert viewer["id"] == "123"
    assert viewer["login"] == "octocat"


@patch("github_bootstrap.github.client.httpx.post")
def test_find_project_found(mock_post: Mock) -> None:
    """find_project() detects an existing project."""

    mock_post.return_value = make_response(
        200,
        {
            "data": {
                "viewer": {
                    "projectsV2": {
                        "nodes": [
                            {
                                "title": "Project A",
                            },
                            {
                                "title": "Bootstrap",
                            },
                        ]
                    }
                }
            }
        },
    )

    client = GitHubClient(token="token")

    project = client.projects.find("Bootstrap")

    assert project.exists is True
    assert project.title == "Bootstrap"


@patch("github_bootstrap.github.client.httpx.post")
def test_find_project_missing(mock_post: Mock) -> None:
    """find_project() returns exists=False."""

    mock_post.return_value = make_response(
        200,
        {"data": {"viewer": {"projectsV2": {"nodes": []}}}},
    )

    client = GitHubClient(token="token")

    project = client.projects.find("Bootstrap")

    assert project.exists is False
