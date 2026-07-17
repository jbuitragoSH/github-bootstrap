"""GitHub Label operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.label_state import LabelSnapshot, LabelState
from github_bootstrap.github.models import GitHubLabel

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
                name
                color
                description
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

        return LabelState(
            labels={
                node["name"]: LabelSnapshot(
                    name=node["name"],
                    color=node["color"],
                    description=node.get("description") or None,
                )
                for node in nodes
            },
        )

    def create(
        self,
        repository_id: str,
        name: str,
        color: str,
        description: str | None = None,
    ) -> GitHubLabel:
        """Create a repository label."""

        mutation = """
        mutation(
          $repositoryId: ID!,
          $name: String!,
          $color: String!,
          $description: String
        ) {
          createLabel(
            input: {
              repositoryId: $repositoryId
              name: $name
              color: $color
              description: $description
            }
          ) {
            label {
              id
              name
            }
          }
        }
        """

        data = self.client.execute(
            mutation,
            {
                "repositoryId": repository_id,
                "name": name,
                "color": color,
                "description": description,
            },
        )

        label = data["createLabel"]["label"]

        return GitHubLabel(
            id=label["id"],
            name=label["name"],
        )
