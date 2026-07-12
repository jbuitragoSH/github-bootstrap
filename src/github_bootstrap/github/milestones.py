"""GitHub Milestone operations."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.github.models import GitHubMilestone

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


class MilestonesAPI:
    """Operations for GitHub repository milestones."""

    def __init__(
        self,
        client: GitHubClient,
    ) -> None:
        self.client = client

    def find(
        self,
        owner: str,
        repository: str,
    ) -> MilestoneState:
        """Load open repository milestones."""

        query = """
        query($owner: String!, $repository: String!) {
          repository(
            owner: $owner,
            name: $repository
          ) {
            milestones(
              first: 100,
              states: [OPEN]
            ) {
              nodes {
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

        nodes = repository_data["milestones"]["nodes"]

        milestones = {node["title"] for node in nodes}

        return MilestoneState(
            milestones=milestones,
        )

    def create(
        self,
        owner: str,
        repository: str,
        title: str,
        description: str | None = None,
        due_on: date | None = None,
    ) -> GitHubMilestone:
        """Create a repository milestone."""

        payload: dict[str, Any] = {
            "title": title,
            "description": description,
            "due_on": _format_due_on(due_on),
        }

        milestone = self.client.execute_rest(
            "POST",
            f"/repos/{owner}/{repository}/milestones",
            payload,
        )

        return GitHubMilestone(
            id=milestone["node_id"],
            title=milestone["title"],
            number=milestone["number"],
        )


def _format_due_on(value: date | None) -> str | None:
    """Convert a milestone date to an ISO 8601 UTC timestamp."""

    if value is None:
        return None

    return f"{value.isoformat()}T23:59:59Z"
