"""GitHub Project item operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient

from github_bootstrap.github.project_item_state import (
    ProjectItemSnapshot,
    ProjectItemState,
)


class ProjectItemsAPI:
    """Operations for GitHub Project V2 items."""

    def __init__(
        self,
        client: GitHubClient,
    ) -> None:
        self.client = client

    def add(
        self,
        project_id: str,
        content_id: str,
    ) -> str:
        """Add repository content to a GitHub Project V2."""

        mutation = """
        mutation(
          $projectId: ID!,
          $contentId: ID!
        ) {
          addProjectV2ItemById(
            input: {
              projectId: $projectId
              contentId: $contentId
            }
          ) {
            item {
              id
            }
          }
        }
        """

        data = self.client.execute(
            mutation,
            {
                "projectId": project_id,
                "contentId": content_id,
            },
        )

        result = data.get("addProjectV2ItemById")

        if not isinstance(result, dict):
            raise GitHubError("Invalid response from GitHub API.")

        item = result.get("item")

        if not isinstance(item, dict):
            raise GitHubError("Invalid response from GitHub API.")

        item_id = item.get("id")

        if not isinstance(item_id, str):
            raise GitHubError("Invalid response from GitHub API.")

        return item_id

    def set_single_select_field(
        self,
        project_id: str,
        item_id: str,
        field_id: str,
        option_id: str,
    ) -> None:
        """Set a single-select field value on a Project V2 item."""

        mutation = """
        mutation(
          $projectId: ID!,
          $itemId: ID!,
          $fieldId: ID!,
          $optionId: String!
        ) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: {
                singleSelectOptionId: $optionId
              }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """

        self.client.execute(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "optionId": option_id,
            },
        )

    def set_text_field(
        self,
        project_id: str,
        item_id: str,
        field_id: str,
        value: str,
    ) -> None:
        """Set a text field value on a Project V2 item."""

        mutation = """
        mutation(
          $projectId: ID!,
          $itemId: ID!,
          $fieldId: ID!,
          $value: String!
        ) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: {
                text: $value
              }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """

        self.client.execute(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "value": value,
            },
        )

    def set_number_field(
        self,
        project_id: str,
        item_id: str,
        field_id: str,
        value: int | float,
    ) -> None:
        """Set a number field value on a Project V2 item."""

        mutation = """
        mutation(
          $projectId: ID!,
          $itemId: ID!,
          $fieldId: ID!,
          $value: Float!
        ) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: {
                number: $value
              }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """

        self.client.execute(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "value": float(value),
            },
        )

    def set_date_field(
        self,
        project_id: str,
        item_id: str,
        field_id: str,
        value: str,
    ) -> None:
        """Set a date field value on a Project V2 item."""

        mutation = """
        mutation(
          $projectId: ID!,
          $itemId: ID!,
          $fieldId: ID!,
          $value: Date!
        ) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: {
                date: $value
              }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """

        self.client.execute(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "value": value,
            },
        )

    def set_iteration_field(
        self,
        project_id: str,
        item_id: str,
        field_id: str,
        iteration_id: str,
    ) -> None:
        """Set an iteration field value on a Project V2 item."""

        mutation = """
        mutation(
          $projectId: ID!,
          $itemId: ID!,
          $fieldId: ID!,
          $iterationId: String!
        ) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: {
                iterationId: $iterationId
              }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """

        self.client.execute(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "iterationId": iteration_id,
            },
        )

    def find(
        self,
        project_id: str,
    ) -> ProjectItemState:
        """Load current items from a GitHub Project V2."""

        query = """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      id
                    }
                  }
                }
              }
            }
          }
        }
        """

        data = self.client.execute(
            query,
            {
                "projectId": project_id,
            },
        )

        project = data.get("node")

        if not isinstance(project, dict):
            raise GitHubError("Invalid response from GitHub API.")

        items_data = project.get("items")

        if not isinstance(items_data, dict):
            raise GitHubError("Invalid response from GitHub API.")

        nodes = items_data.get("nodes")

        if not isinstance(nodes, list):
            raise GitHubError("Invalid response from GitHub API.")

        items: dict[str, ProjectItemSnapshot] = {}

        for node in nodes:
            if not isinstance(node, dict):
                continue

            item_id = node.get("id")
            content = node.get("content")

            if not isinstance(item_id, str):
                continue

            if not isinstance(content, dict):
                continue

            content_id = content.get("id")

            if not isinstance(content_id, str):
                continue

            items[content_id] = ProjectItemSnapshot(
                id=item_id,
                content_id=content_id,
            )

        return ProjectItemState(
            items=items,
        )
