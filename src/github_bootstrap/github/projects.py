"""GitHub Project operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.models import GitHubProject
from github_bootstrap.github.state import ProjectState

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


class ProjectsAPI:
    """Operations for GitHub Projects V2."""

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def find(
        self,
        title: str,
    ) -> ProjectState:
        """Find a GitHub Project V2 by title."""

        query = """
        query {
          viewer {
            projectsV2(first: 100) {
              nodes {
                title
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
            if project["title"] == title:
                return ProjectState(
                    exists=True,
                    title=title,
                )

        return ProjectState(
            exists=False,
            title=title,
        )

    def create(
        self,
        owner_id: str,
        title: str,
    ) -> GitHubProject:
        """Create a GitHub Project V2."""

        mutation = """
        mutation($ownerId: ID!, $title: String!) {
          createProjectV2(
            input: {
              ownerId: $ownerId
              title: $title
            }
          ) {
            projectV2 {
              id
              title
            }
          }
        }
        """

        data = self.client.execute(
            mutation,
            {
                "ownerId": owner_id,
                "title": title,
            },
        )

        project = data["createProjectV2"]["projectV2"]

        return GitHubProject(
            id=project["id"],
            title=project["title"],
        )
