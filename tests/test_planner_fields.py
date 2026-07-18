from github_bootstrap.github.field_state import (
    FieldOptionSnapshot,
    FieldSnapshot,
    FieldState,
)
from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.github.issue_state import IssueState
from github_bootstrap.github.label_state import LabelState
from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.github.project_item_state import ProjectItemState
from github_bootstrap.github.state import ProjectState
from github_bootstrap.planner.fields import plan_fields
from github_bootstrap.planner.plan import create_plan
from github_bootstrap.specification.models import (
    DateField,
    IterationField,
    NumberField,
    Project,
    ProjectSpecification,
    SingleSelectField,
    TextField,
)


def test_plan_fields_creates_missing_fields() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=[
            TextField(
                name="Component",
            ),
            NumberField(
                name="Story Points",
            ),
            DateField(
                name="Due Date",
            ),
            SingleSelectField(
                name="Priority",
                options=[
                    "Low",
                    "Medium",
                    "High",
                ],
            ),
            IterationField(
                name="Sprint",
            ),
        ],
    )

    state = FieldState(
        fields={
            "Component": FieldSnapshot(
                id="field-component",
                name="Component",
                data_type="TEXT",
            ),
            "Story Points": FieldSnapshot(
                id="field-story-points",
                name="Story Points",
                data_type="NUMBER",
            ),
        },
    )

    actions = plan_fields(
        specification,
        state,
    )

    assert len(actions) == 3

    assert actions[0].operation == "create"
    assert actions[0].resource == "field"
    assert actions[0].description == "Create date field 'Due Date'"
    assert actions[0].payload == {
        "name": "Due Date",
        "data_type": "DATE",
    }

    assert actions[1].operation == "create"
    assert actions[1].resource == "field"
    assert actions[1].description == ("Create single-select field 'Priority'")
    assert actions[1].payload == {
        "name": "Priority",
        "data_type": "SINGLE_SELECT",
        "options": [
            "Low",
            "Medium",
            "High",
        ],
    }

    assert actions[2].operation == "create"
    assert actions[2].resource == "field"
    assert actions[2].description == "Create iteration field 'Sprint'"
    assert actions[2].payload == {
        "name": "Sprint",
        "data_type": "ITERATION",
    }


def test_plan_fields_returns_no_actions_when_all_fields_exist() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=[
            TextField(
                name="Component",
            ),
            NumberField(
                name="Story Points",
            ),
        ],
    )

    state = FieldState(
        fields={
            "Component": FieldSnapshot(
                id="field-component",
                name="Component",
                data_type="TEXT",
            ),
            "Story Points": FieldSnapshot(
                id="field-story-points",
                name="Story Points",
                data_type="NUMBER",
            ),
        },
    )

    actions = plan_fields(
        specification,
        state,
    )

    assert actions == []


def test_create_plan_includes_missing_fields() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=[
            TextField(
                name="Component",
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

    field_actions = [action for action in plan.actions if action.resource == "field"]

    assert len(field_actions) == 1
    assert field_actions[0].description == "Create text field 'Component'"
    assert field_actions[0].payload == {
        "name": "Component",
        "data_type": "TEXT",
    }


def test_plan_fields_skips_existing_fields() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=[
            SingleSelectField(
                name="Status",
                options=["Todo", "Done"],
            ),
            SingleSelectField(
                name="Priority",
                options=["Low", "Medium", "High"],
            ),
        ],
    )

    state = FieldState(
        fields={
            "Status": FieldSnapshot(
                id="field-status",
                name="Status",
                data_type="SINGLE_SELECT",
                options=(
                    FieldOptionSnapshot(
                        id="option-todo",
                        name="Todo",
                    ),
                    FieldOptionSnapshot(
                        id="option-done",
                        name="Done",
                    ),
                ),
            ),
            "Priority": FieldSnapshot(
                id="field-priority",
                name="Priority",
                data_type="SINGLE_SELECT",
                options=(
                    FieldOptionSnapshot(
                        id="option-low",
                        name="Low",
                    ),
                    FieldOptionSnapshot(
                        id="option-medium",
                        name="Medium",
                    ),
                    FieldOptionSnapshot(
                        id="option-high",
                        name="High",
                    ),
                ),
            ),
        },
    )

    actions = plan_fields(specification, state)

    assert actions == []


def test_plan_fields_is_case_insensitive() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=[
            SingleSelectField(
                name="status",
                options=["Todo", "Done"],
            ),
        ],
    )

    state = FieldState(
        fields={
            "Status": FieldSnapshot(
                id="field-status",
                name="Status",
                data_type="SINGLE_SELECT",
                options=(
                    FieldOptionSnapshot(
                        id="option-todo",
                        name="Todo",
                    ),
                    FieldOptionSnapshot(
                        id="option-done",
                        name="Done",
                    ),
                ),
            ),
        },
    )

    actions = plan_fields(specification, state)

    assert actions == []


def test_plan_fields_detects_type_drift() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=[
            NumberField(
                name="Priority",
            ),
        ],
    )

    state = FieldState(
        fields={
            "Priority": FieldSnapshot(
                id="field-priority",
                name="Priority",
                data_type="SINGLE_SELECT",
                options=(
                    FieldOptionSnapshot(
                        id="option-low",
                        name="Low",
                    ),
                    FieldOptionSnapshot(
                        id="option-high",
                        name="High",
                    ),
                ),
            ),
        },
    )

    actions = plan_fields(specification, state)

    assert len(actions) == 1
    assert actions[0].operation == "drift"
    assert actions[0].resource == "field"
    assert actions[0].description == (
        "Field 'Priority' exists with drift: type differs"
    )


def test_plan_fields_detects_single_select_option_drift() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        fields=[
            SingleSelectField(
                name="Priority",
                options=["Low", "Medium", "High"],
            ),
        ],
    )

    state = FieldState(
        fields={
            "Priority": FieldSnapshot(
                id="field-priority",
                name="Priority",
                data_type="SINGLE_SELECT",
                options=(
                    FieldOptionSnapshot(
                        id="option-low",
                        name="Low",
                    ),
                    FieldOptionSnapshot(
                        id="option-high",
                        name="High",
                    ),
                ),
            ),
        },
    )

    actions = plan_fields(specification, state)

    assert len(actions) == 1
    assert actions[0].operation == "drift"
    assert actions[0].resource == "field"
    assert actions[0].description == (
        "Field 'Priority' exists with drift: options differ"
    )
