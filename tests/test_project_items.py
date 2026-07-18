from unittest.mock import MagicMock

from github_bootstrap.github.project_items import ProjectItemsAPI


def test_add_issue_to_project() -> None:
    client = MagicMock()

    client.execute.return_value = {
        "addProjectV2ItemById": {
            "item": {
                "id": "project-item-id",
            },
        },
    }

    api = ProjectItemsAPI(client)

    item_id = api.add(
        project_id="project-id",
        content_id="issue-node-id",
    )

    assert item_id == "project-item-id"
    client.execute.assert_called_once()
