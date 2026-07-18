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


def test_set_text_field() -> None:
    client = MagicMock()

    api = ProjectItemsAPI(client)

    api.set_text_field(
        project_id="project-id",
        item_id="item-id",
        field_id="field-id",
        value="AG-001",
    )

    client.execute.assert_called_once()


def test_set_number_field() -> None:
    client = MagicMock()

    api = ProjectItemsAPI(client)

    api.set_number_field(
        project_id="project-id",
        item_id="item-id",
        field_id="field-id",
        value=5,
    )

    client.execute.assert_called_once()


def test_set_date_field() -> None:
    client = MagicMock()

    api = ProjectItemsAPI(client)

    api.set_date_field(
        project_id="project-id",
        item_id="item-id",
        field_id="field-id",
        value="2026-08-15",
    )

    client.execute.assert_called_once()


def test_set_iteration_field() -> None:
    client = MagicMock()

    api = ProjectItemsAPI(client)

    api.set_iteration_field(
        project_id="project-id",
        item_id="item-id",
        field_id="field-id",
        iteration_id="iteration-id",
    )

    client.execute.assert_called_once()
