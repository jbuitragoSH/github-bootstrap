"""GitHub GraphQL client."""

import os
from typing import Any

import httpx

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.labels import LabelsAPI
from github_bootstrap.github.projects import ProjectsAPI


class GitHubClient:
    """Minimal GitHub GraphQL client."""

    API_URL = "https://api.github.com/graphql"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.projects: ProjectsAPI = ProjectsAPI(self)
        self.labels: LabelsAPI = LabelsAPI(self)
        if not self.token:
            raise GitHubError("GITHUB_TOKEN environment variable is required.")

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL operation."""

        response = httpx.post(
            self.API_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
            },
            json={
                "query": query,
                "variables": variables or {},
            },
            timeout=10.0,
        )

        if response.status_code != 200:
            raise GitHubError(f"GitHub request failed: {response.status_code}")

        payload: dict[str, Any] = response.json()

        if "errors" in payload:
            messages = ", ".join(error["message"] for error in payload["errors"])
            raise GitHubError(messages)

        data = payload.get("data")

        if not isinstance(data, dict):
            raise GitHubError("Invalid response from GitHub API.")

        return data

    def viewer(self) -> dict[str, Any]:
        """Return authenticated GitHub user information."""
        query = """
        query {
        viewer {
            id
            login
        }
        }
        """

        data = self.execute(query)

        viewer = data.get("viewer")

        if not isinstance(viewer, dict):
            raise GitHubError("Invalid response from GitHub API.")

        return viewer
