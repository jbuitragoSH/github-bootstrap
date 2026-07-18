"""GitHub Project field operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from github_bootstrap.github.exceptions import GitHubError
from github_bootstrap.github.field_state import (
    FieldOptionSnapshot,
    FieldSnapshot,
    FieldState,
    IterationSnapshot,
)

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
                    __typename
                    ... on ProjectV2Field {
                      id
                      name
                      dataType
                    }
                    ... on ProjectV2SingleSelectField {
                      id
                      name
                      dataType
                      options {
                        id
                        name
                      }
                    }
                    ... on ProjectV2IterationField {
                      id
                      name
                      dataType
                      configuration {
                        iterations {
                          id
                          title
                          startDate
                          duration
                        }
                      }
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
                fields={node["name"]: _to_field_snapshot(node) for node in nodes},
            )

        return FieldState(fields={})

    def create(
        self,
        project_id: str,
        name: str,
        data_type: str,
        options: list[str] | None = None,
    ) -> None:
        """Create a project field."""

        variables: dict[str, Any]

        if data_type == "SINGLE_SELECT":
            mutation = """
            mutation(
              $projectId: ID!,
              $name: String!,
              $options: [ProjectV2SingleSelectFieldOptionInput!]!
            ) {
              createProjectV2Field(
                input: {
                  projectId: $projectId
                  name: $name
                  dataType: SINGLE_SELECT
                  singleSelectOptions: $options
                }
              ) {
                projectV2Field {
                  ... on ProjectV2FieldCommon {
                    id
                    name
                  }
                }
              }
            }
            """

            variables = {
                "projectId": project_id,
                "name": name,
                "options": [
                    {
                        "name": option,
                        "color": "GRAY",
                        "description": "",
                    }
                    for option in (options or [])
                ],
            }

            self.client.execute(mutation, variables)
            return

        if data_type == "ITERATION":
            mutation = """
            mutation(
              $projectId: ID!,
              $name: String!,
              $configuration: ProjectV2IterationFieldConfigurationInput!
            ) {
              createProjectV2Field(
                input: {
                  projectId: $projectId
                  name: $name
                  dataType: ITERATION
                  iterationConfiguration: $configuration
                }
              ) {
                projectV2Field {
                  ... on ProjectV2FieldCommon {
                    id
                    name
                  }
                }
              }
            }
            """

            start_date = datetime.now(timezone.utc).date().isoformat()

            variables = {
                "projectId": project_id,
                "name": name,
                "configuration": {
                    "duration": 14,
                    "startDate": start_date,
                    "iterations": [],
                },
            }

            self.client.execute(mutation, variables)
            return

        mutation = """
        mutation(
          $projectId: ID!,
          $name: String!,
          $dataType: ProjectV2CustomFieldType!
        ) {
          createProjectV2Field(
            input: {
              projectId: $projectId
              name: $name
              dataType: $dataType
            }
          ) {
            projectV2Field {
              ... on ProjectV2FieldCommon {
                id
                name
              }
            }
          }
        }
        """

        variables = {
            "projectId": project_id,
            "name": name,
            "dataType": data_type,
        }

        self.client.execute(mutation, variables)


def _to_field_snapshot(
    node: dict[str, Any],
) -> FieldSnapshot:
    """Convert a GraphQL field node into a field snapshot."""

    typename = node["__typename"]

    if typename == "ProjectV2SingleSelectField":
        return FieldSnapshot(
            id=node["id"],
            name=node["name"],
            data_type=node["dataType"],
            options=tuple(
                FieldOptionSnapshot(
                    id=option["id"],
                    name=option["name"],
                )
                for option in node.get("options", [])
            ),
        )

    if typename == "ProjectV2IterationField":
        configuration = node.get("configuration", {})

        return FieldSnapshot(
            id=node["id"],
            name=node["name"],
            data_type=node["dataType"],
            iterations=tuple(
                IterationSnapshot(
                    id=iteration["id"],
                    title=iteration["title"],
                )
                for iteration in configuration.get("iterations", [])
            ),
        )

    return FieldSnapshot(
        id=node["id"],
        name=node["name"],
        data_type=node["dataType"],
    )
