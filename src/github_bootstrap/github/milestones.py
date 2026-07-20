"""GitHub milestone operations."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.milestone_state import (
    MilestoneSnapshot,
    MilestoneState,
)
from github_bootstrap.github.models import GitHubMilestone

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


class MilestonesAPI:
    """Operations for GitHub milestones."""

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
                number
                title
                description
                dueOn
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

        return MilestoneState(
            milestones={
                node["title"]: MilestoneSnapshot(
                    title=node["title"],
                    number=node["number"],
                    description=node.get("description") or None,
                    due_on=_parse_due_on(node.get("dueOn")),
                )
                for node in nodes
            },
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

        response = self.client.execute_rest(
            "POST",
            f"/repos/{owner}/{repository}/milestones",
            payload,
        )

        return GitHubMilestone(
            id=response["node_id"],
            number=response["number"],
            title=response["title"],
        )


def _format_due_on(due_on: date | str | None) -> str | None:
    """Format a milestone due date for the GitHub REST API."""

    if due_on is None:
        return None

    if isinstance(due_on, date):
        return f"{due_on.isoformat()}T23:59:59Z"

    if "T" not in due_on:
        return f"{due_on}T23:59:59Z"

    return due_on


def _parse_due_on(
    value: str | None,
) -> date | None:
    """Parse a GitHub milestone due date."""

    if value is None:
        return None

    return date.fromisoformat(value[:10])
