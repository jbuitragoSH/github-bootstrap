"""GitHub Label operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.label_state import LabelState

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


class LabelsAPI:
    """Operations for GitHub repository labels."""

    def __init__(
        self,
        client: GitHubClient,
    ) -> None:
        self.client = client

    def find(
        self,
        owner: str,
        repository: str,
    ) -> LabelState:
        """Load repository labels."""

        query = """
        query($owner: String!, $repository: String!) {
        repository(
            owner: $owner,
            name: $repository
        ) {
            labels(first: 100) {
            nodes {
                id
                name
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

        nodes = repository_data["labels"]["nodes"]

        labels = {node["name"] for node in nodes}

        return LabelState(
            labels=labels,
        )
