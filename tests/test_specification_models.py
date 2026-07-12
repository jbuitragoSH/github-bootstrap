from datetime import date

from github_bootstrap.specification.models import (
    Milestone,
    Project,
    ProjectSpecification,
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
