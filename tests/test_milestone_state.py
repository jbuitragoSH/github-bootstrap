from datetime import date

from github_bootstrap.github.field_state import FieldState
from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.github.issue_state import IssueState
from github_bootstrap.github.label_state import LabelState
from github_bootstrap.github.milestone_state import (
    MilestoneSnapshot,
    MilestoneState,
)
from github_bootstrap.github.project_item_state import ProjectItemState
from github_bootstrap.github.state import ProjectState


def test_milestone_state_contains_existing_milestones() -> None:
    state = MilestoneState(
        milestones={
            "Sprint 1": MilestoneSnapshot(
                title="Sprint 1",
                number=1,
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
            "Sprint 2": MilestoneSnapshot(
                title="Sprint 2",
                number=2,
                description="Advanced features",
                due_on=date(2026, 8, 31),
            ),
        },
    )

    assert set(state.milestones) == {
        "Sprint 1",
        "Sprint 2",
    }
    assert state.milestones["Sprint 1"].number == 1
    assert state.milestones["Sprint 1"].description == "Foundation capabilities"
    assert state.milestones["Sprint 1"].due_on == date(2026, 7, 31)


def test_github_state_contains_milestone_state() -> None:
    milestone_state = MilestoneState(
        milestones={
            "Sprint 1": MilestoneSnapshot(
                title="Sprint 1",
                number=1,
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        },
    )

    state = GitHubState(
        project=ProjectState(
            exists=True,
            title="Project",
            id=None,
        ),
        labels=LabelState(
            labels={},
        ),
        milestones=milestone_state,
        fields=FieldState(
            fields={},
        ),
        issues=IssueState(
            issues={},
        ),
        project_items=ProjectItemState(
            items={},
        ),
    )

    assert state.milestones is milestone_state
    assert set(state.milestones.milestones) == {"Sprint 1"}
    assert state.milestones.milestones["Sprint 1"].number == 1
    assert state.milestones.milestones["Sprint 1"].due_on == date(2026, 7, 31)
