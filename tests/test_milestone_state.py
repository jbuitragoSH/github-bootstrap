from github_bootstrap.github.field_state import FieldState
from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.github.label_state import LabelState
from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.github.state import ProjectState


def test_milestone_state_contains_existing_milestones() -> None:
    state = MilestoneState(
        milestones={
            "Sprint 1",
            "Sprint 2",
        },
    )

    assert state.milestones == {
        "Sprint 1",
        "Sprint 2",
    }


def test_github_state_contains_milestone_state() -> None:
    milestone_state = MilestoneState(
        milestones={"Sprint 1"},
    )

    state = GitHubState(
        project=ProjectState(
            exists=True,
            title="Project",
        ),
        labels=LabelState(
            labels=set(),
        ),
        milestones=milestone_state,
        fields=FieldState(
            fields=set(),
        ),
    )

    assert state.milestones is milestone_state
    assert state.milestones.milestones == {"Sprint 1"}
