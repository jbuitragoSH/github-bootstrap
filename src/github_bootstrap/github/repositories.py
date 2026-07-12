"""GitHub Repository operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.models import GitHubRepository

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


class RepositoriesAPI:
    """Operations for GitHub repositories."""

    def __init__(
        self,
        client: GitHubClient,
    ) -> None:
        self.client = client

    def find(
        self,
        owner: str,
        repository: str,
    ) -> GitHubRepository:
        """Find a GitHub repository."""

        query = """
        query($owner: String!, $repository: String!) {
          repository(
            owner: $owner,
            name: $repository
          ) {
            id
            name
          }
        }
        """

        data = self.client.execute(
            query,
            {
                "owner": owner,
                "repository": repository,
            },
        )

        repository_data = data.get("repository")

        if not isinstance(repository_data, dict):
            raise GitHubError("Repository not found.")

        return GitHubRepository(
            id=repository_data["id"],
            name=repository_data["name"],
        )
