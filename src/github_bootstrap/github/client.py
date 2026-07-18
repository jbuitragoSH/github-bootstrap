"""GitHub API client."""

import os
from typing import Any

import httpx

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.fields import FieldsAPI
from github_bootstrap.github.issues import IssuesAPI
from github_bootstrap.github.labels import LabelsAPI
from github_bootstrap.github.milestones import MilestonesAPI
from github_bootstrap.github.project_items import ProjectItemsAPI
from github_bootstrap.github.projects import ProjectsAPI
from github_bootstrap.github.repositories import RepositoriesAPI


class GitHubClient:
    """GitHub GraphQL and REST API client."""

    API_URL = "https://api.github.com/graphql"
    REST_API_URL = "https://api.github.com"
    REST_API_VERSION = "2026-03-10"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")

        self.projects = ProjectsAPI(self)
        self.labels = LabelsAPI(self)
        self.milestones = MilestonesAPI(self)
        self.repositories = RepositoriesAPI(self)
        self.fields = FieldsAPI(self)
        self.issues = IssuesAPI(self)
        self.project_items = ProjectItemsAPI(self)
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

    def execute_rest(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a GitHub REST API operation."""

        response = httpx.request(
            method,
            f"{self.REST_API_URL}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": self.REST_API_VERSION,
            },
            json=payload,
            timeout=10.0,
        )

        if not 200 <= response.status_code < 300:
            raise GitHubError(f"GitHub request failed: {response.status_code}")

        data: Any = response.json()

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
