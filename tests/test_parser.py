from datetime import date

from github_bootstrap.specification.models import (
    DateField,
    IterationField,
    NumberField,
    SingleSelectField,
    TextField,
)
from github_bootstrap.specification.parser import parse_specification


def test_parse_specification_with_labels() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "labels": [
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Bug report",
            },
            {
                "name": "documentation",
                "color": "0075ca",
            },
        ],
    }

    result = parse_specification(specification)

    assert result.organization == "org"
    assert result.repository == "repo"
    assert result.project.title == "Project"

    assert len(result.labels) == 2

    assert result.labels[0].name == "bug"
    assert result.labels[0].color == "d73a4a"
    assert result.labels[0].description == "Bug report"

    assert result.labels[1].name == "documentation"
    assert result.labels[1].color == "0075ca"
    assert result.labels[1].description is None


def test_parse_specification_with_milestones() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "milestones": [
            {
                "title": "Sprint 1",
                "description": "Foundation capabilities",
                "due_on": "2026-07-31",
            },
            {
                "title": "Sprint 2",
            },
        ],
    }

    result = parse_specification(specification)

    assert len(result.milestones) == 2

    assert result.milestones[0].title == "Sprint 1"
    assert result.milestones[0].description == "Foundation capabilities"
    assert result.milestones[0].due_on == date(2026, 7, 31)

    assert result.milestones[1].title == "Sprint 2"
    assert result.milestones[1].description is None
    assert result.milestones[1].due_on is None


def test_parse_specification_with_yaml_date_milestone() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "milestones": [
            {
                "title": "Sprint 1",
                "due_on": date(2026, 7, 31),
            },
        ],
    }

    result = parse_specification(specification)

    assert result.milestones[0].due_on == date(2026, 7, 31)


def test_parse_specification_without_milestones() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
    }

    result = parse_specification(specification)

    assert result.milestones == []


def test_parse_specification_with_fields() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "name": "Component",
                "type": "text",
            },
            {
                "name": "Story Points",
                "type": "number",
            },
            {
                "name": "Due Date",
                "type": "date",
            },
            {
                "name": "Priority",
                "type": "single_select",
                "options": [
                    "Low",
                    "Medium",
                    "High",
                ],
            },
            {
                "name": "Sprint",
                "type": "iteration",
            },
        ],
    }

    result = parse_specification(specification)

    assert len(result.fields) == 5

    assert result.fields[0] == TextField(
        name="Component",
    )

    assert result.fields[1] == NumberField(
        name="Story Points",
    )

    assert result.fields[2] == DateField(
        name="Due Date",
    )

    assert result.fields[3] == SingleSelectField(
        name="Priority",
        options=[
            "Low",
            "Medium",
            "High",
        ],
    )

    assert result.fields[4] == IterationField(
        name="Sprint",
    )


def test_parse_single_select_field_without_options() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "name": "Priority",
                "type": "single_select",
            },
        ],
    }

    result = parse_specification(specification)

    assert result.fields == [
        SingleSelectField(
            name="Priority",
            options=[],
        ),
    ]


def test_parse_specification_without_fields() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
    }

    result = parse_specification(specification)

    assert result.fields == []
