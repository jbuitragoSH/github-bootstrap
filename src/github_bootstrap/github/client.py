"""GitHub GraphQL client."""

import os
from typing import Any

import httpx


class GitHubError(Exception):
    """Raised when GitHub communication fails."""


class GitHubClient:
    """Minimal GitHub GraphQL client."""

    API_URL = "https://api.github.com/graphql"

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")

        if not self.token:
            raise GitHubError("GITHUB_TOKEN environment variable is required.")

    def viewer(self) -> dict[str, Any]:
        """Return authenticated GitHub user information."""
        query = """
        query {
        viewer {
            login
        }
        }
        """

        response = httpx.post(
            self.API_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
            },
            json={"query": query},
            timeout=10.0,
        )

        if response.status_code != 200:
            raise GitHubError(f"GitHub request failed: {response.status_code}")

        data: dict[str, Any] = response.json()

        if "errors" in data:
            raise GitHubError(str(data["errors"]))

        viewer = data.get("data", {}).get("viewer")

        if not isinstance(viewer, dict):
            raise GitHubError("Invalid response from GitHub API.")

        return viewer
