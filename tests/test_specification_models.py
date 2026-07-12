from datetime import date

from github_bootstrap.specification.models import (
    DateField,
    IterationField,
    Milestone,
    NumberField,
    Project,
    ProjectSpecification,
    SingleSelectField,
    TextField,
)


def test_create_milestone_with_all_fields() -> None:
    milestone = Milestone(
        title="Sprint 1",
        description="Foundation capabilities",
        due_on=date(2026, 7, 31),
    )

    assert milestone.title == "Sprint 1"
    assert milestone.description == "Foundation capabilities"
    assert milestone.due_on == date(2026, 7, 31)


def test_create_milestone_with_optional_fields_omitted() -> None:
    milestone = Milestone(
        title="Sprint 1",
    )

    assert milestone.title == "Sprint 1"
    assert milestone.description is None
    assert milestone.due_on is None


def test_project_specification_contains_milestones() -> None:
    milestone = Milestone(
        title="Sprint 1",
        description="Foundation capabilities",
        due_on=date(2026, 7, 31),
    )

    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        milestones=[milestone],
    )

    assert specification.milestones == [milestone]


def test_project_specification_has_empty_milestones_by_default() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
    )

    assert specification.milestones == []


def test_create_text_field() -> None:
    project_field = TextField(
        name="Component",
    )

    assert project_field.name == "Component"


def test_create_number_field() -> None:
    project_field = NumberField(
        name="Story Points",
    )

    assert project_field.name == "Story Points"


def test_create_date_field() -> None:
    project_field = DateField(
        name="Due Date",
    )

    assert project_field.name == "Due Date"


def test_create_single_select_field() -> None:
    project_field = SingleSelectField(
        name="Priority",
        options=[
            "Low",
            "Medium",
            "High",
        ],
    )

    assert project_field.name == "Priority"
    assert project_field.options == [
        "Low",
        "Medium",
        "High",
    ]


def test_single_select_field_has_empty_options_by_default() -> None:
    project_field = SingleSelectField(
        name="Priority",
    )

    assert project_field.options == []


def test_create_iteration_field() -> None:
    project_field = IterationField(
        name="Iteration",
    )

    assert project_field.name == "Iteration"


def test_project_specification_contains_fields() -> None:
    fields = [
        TextField(name="Component"),
        NumberField(name="Story Points"),
        DateField(name="Due Date"),
        SingleSelectField(
            name="Priority",
            options=[
                "Low",
                "Medium",
                "High",
            ],
        ),
        IterationField(name="Iteration"),
    ]

    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=fields,
    )

    assert specification.fields == fields


def test_project_specification_has_empty_fields_by_default() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
    )

    assert specification.fields == []
