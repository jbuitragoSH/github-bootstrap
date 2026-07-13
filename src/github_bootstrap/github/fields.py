"""GitHub Project field operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.field_state import FieldState

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


class FieldsAPI:
    """Operations for GitHub Project fields."""

    def __init__(
        self,
        client: GitHubClient,
    ) -> None:
        self.client = client

    def find(
        self,
        project_title: str,
    ) -> FieldState:
        """Load fields from a GitHub Project V2."""

        query = """
        query {
          viewer {
            projectsV2(first: 100) {
              nodes {
                title
                fields(first: 100) {
                  nodes {
                    ... on ProjectV2FieldCommon {
                      name
                    }
                  }
                }
              }
            }
          }
        }
        """

        data = self.client.execute(query)

        viewer = data.get("viewer")

        if not isinstance(viewer, dict):
            raise GitHubError("Invalid response from GitHub API.")

        projects = viewer["projectsV2"]["nodes"]

        for project in projects:
            if project["title"] != project_title:
                continue

            nodes = project["fields"]["nodes"]

            return FieldState(
                fields={node["name"] for node in nodes},
            )

        return FieldState(
            fields=set(),
        )
