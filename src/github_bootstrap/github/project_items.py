"""GitHub Project item operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from github_bootstrap.github.exceptions import GitHubError

if TYPE_CHECKING:
    from github_bootstrap.github.client import GitHubClient


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
