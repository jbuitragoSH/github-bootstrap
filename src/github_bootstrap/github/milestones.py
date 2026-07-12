"""GitHub Milestone operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.milestone_state import MilestoneState

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
