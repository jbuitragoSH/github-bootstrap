"""GitHub issue operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.issue_state import (
    IssueSnapshot,
    IssueState,
)

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


class IssuesAPI:
    """Operations for GitHub repository issues."""

    def __init__(
        self,
        client: GitHubClient,
    ) -> None:
        self.client = client

    def find(
        self,
        owner: str,
        repository: str,
    ) -> IssueState:
        """Load open repository issues."""

        query = """
        query($owner: String!, $repository: String!) {
          repository(
            owner: $owner,
            name: $repository
          ) {
            issues(
              first: 100,
              states: [OPEN]
            ) {
              nodes {
                id
                number
                title
              }
            }
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
            raise GitHubError("Invalid response from GitHub API.")

        nodes = repository_data["issues"]["nodes"]

        return IssueState(
            issues={
                node["id"]: IssueSnapshot(
                    id=node["id"],
                    number=node["number"],
                    title=node["title"],
                )
                for node in nodes
            },
        )

    def create(
        self,
        owner: str,
        repository: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        milestone: int | None = None,
    ) -> IssueSnapshot:
        """Create a repository issue."""

        payload: dict[str, Any] = {
            "title": title,
            "body": body,
            "labels": labels or [],
        }

        if milestone is not None:
            payload["milestone"] = milestone

        response = self.client.execute_rest(
            "POST",
            f"/repos/{owner}/{repository}/issues",
            payload,
        )

        return IssueSnapshot(
            id=response["node_id"],
            number=response["number"],
            title=response["title"],
        )
