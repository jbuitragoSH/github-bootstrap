from datetime import date

from github_bootstrap.github.field_state import FieldState
from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.github.issue_state import IssueState
from github_bootstrap.github.label_state import LabelState
from github_bootstrap.github.milestone_state import MilestoneSnapshot, MilestoneState
from github_bootstrap.github.project_item_state import ProjectItemState
from github_bootstrap.github.state import ProjectState
from github_bootstrap.planner.milestones import plan_milestones
from github_bootstrap.planner.plan import create_plan
from github_bootstrap.specification.models import (
    Milestone,
    Project,
    ProjectSpecification,
)


def test_plan_milestones_creates_missing_milestones() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        milestones=[
            Milestone(
                title="Sprint 1",
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
            Milestone(
                title="Sprint 2",
                description=None,
                due_on=None,
            ),
        ],
    )

    state = MilestoneState(
        milestones={
            "Sprint 1": MilestoneSnapshot(
                title="Sprint 1",
                number=1,
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        },
    )

    actions = plan_milestones(
        specification,
        state,
    )

    assert len(actions) == 1

    action = actions[0]

    assert action.operation == "create"
    assert action.resource == "milestone"
    assert action.description == "Create milestone 'Sprint 2'"

    assert action.payload["title"] == "Sprint 2"
    assert action.payload["description"] is None
    assert action.payload["due_on"] is None


def test_plan_milestones_returns_no_actions_when_all_exist() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        milestones=[
            Milestone(
                title="Sprint 1",
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        ],
    )

    state = MilestoneState(
        milestones={
            "Sprint 1": MilestoneSnapshot(
                title="Sprint 1",
                number=1,
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        },
    )

    actions = plan_milestones(
        specification,
        state,
    )

    assert actions == []


def test_create_plan_includes_missing_milestones() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        milestones=[
            Milestone(
                title="Sprint 1",
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        ],
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
        milestones=MilestoneState(
            milestones={},
        ),
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

    plan = create_plan(
        specification,
        state,
    )

    milestone_actions = [
        action for action in plan.actions if action.resource == "milestone"
    ]

    assert len(milestone_actions) == 1
    assert milestone_actions[0].description == "Create milestone 'Sprint 1'"


def test_plan_milestones_detects_description_drift() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        milestones=[
            Milestone(
                title="Sprint 1",
                description="Expected description",
                due_on=date(2026, 7, 31),
            ),
        ],
    )

    state = MilestoneState(
        milestones={
            "Sprint 1": MilestoneSnapshot(
                title="Sprint 1",
                number=1,
                description="Current description",
                due_on=date(2026, 7, 31),
            ),
        },
    )

    actions = plan_milestones(
        specification,
        state,
    )

    assert len(actions) == 1
    assert actions[0].operation == "drift"
    assert actions[0].resource == "milestone"
    assert actions[0].description == (
        "Milestone 'Sprint 1' exists with drift: description differs"
    )


def test_plan_milestones_detects_due_date_drift() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        milestones=[
            Milestone(
                title="Sprint 1",
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        ],
    )

    state = MilestoneState(
        milestones={
            "Sprint 1": MilestoneSnapshot(
                title="Sprint 1",
                number=1,
                description="Foundation capabilities",
                due_on=date(2026, 8, 15),
            ),
        },
    )

    actions = plan_milestones(
        specification,
        state,
    )

    assert len(actions) == 1
    assert actions[0].operation == "drift"
    assert actions[0].resource == "milestone"
    assert actions[0].description == (
        "Milestone 'Sprint 1' exists with drift: due date differs"
    )


def test_plan_milestones_is_case_insensitive() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        milestones=[
            Milestone(
                title="sprint 1",
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        ],
    )

    state = MilestoneState(
        milestones={
            "Sprint 1": MilestoneSnapshot(
                title="Sprint 1",
                number=1,
                description="Foundation capabilities",
                due_on=date(2026, 7, 31),
            ),
        },
    )

    actions = plan_milestones(
        specification,
        state,
    )

    assert actions == []
