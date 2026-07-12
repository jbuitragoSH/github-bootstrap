from github_bootstrap.github.models import (
    GitHubLabel,
    GitHubMilestone,
    GitHubProject,
    GitHubRepository,
)


def test_create_github_project() -> None:
    project = GitHubProject(
        id="project-id",
        title="Project",
    )

    assert project.id == "project-id"
    assert project.title == "Project"


def test_create_github_repository() -> None:
    repository = GitHubRepository(
        id="repository-id",
        name="github-bootstrap",
    )

    assert repository.id == "repository-id"
    assert repository.name == "github-bootstrap"


def test_create_github_label() -> None:
    label = GitHubLabel(
        id="label-id",
        name="documentation",
    )

    assert label.id == "label-id"
    assert label.name == "documentation"


def test_create_github_milestone() -> None:
    milestone = GitHubMilestone(
        id="milestone-id",
        title="Sprint 1",
        number=1,
    )

    assert milestone.id == "milestone-id"
    assert milestone.title == "Sprint 1"
    assert milestone.number == 1
