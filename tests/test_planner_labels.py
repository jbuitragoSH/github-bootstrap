from github_bootstrap.github.label_state import LabelSnapshot, LabelState
from github_bootstrap.planner.labels import plan_labels
from github_bootstrap.specification.models import (
    Label,
    Project,
    ProjectSpecification,
)


def test_plan_labels_creates_missing_labels() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        labels=[
            Label(
                name="bug",
                color="d73a4a",
                description="Bug report",
            ),
            Label(
                name="documentation",
                color="0075ca",
                description=None,
            ),
        ],
    )

    state = LabelState(
        labels={
            "bug": LabelSnapshot(
                name="bug",
                color="d73a4a",
                description="Bug report",
            ),
        },
    )

    actions = plan_labels(
        specification,
        state,
    )

    assert len(actions) == 1

    action = actions[0]

    assert action.operation == "create"
    assert action.resource == "label"

    assert action.payload["name"] == "documentation"
    assert action.payload["color"] == "0075ca"
    assert action.payload["description"] is None


def test_plan_labels_detects_color_drift() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        labels=[
            Label(
                name="bug",
                color="ff0000",
                description="Something is not working",
            ),
        ],
    )

    state = LabelState(
        labels={
            "bug": LabelSnapshot(
                name="bug",
                color="d73a4a",
                description="Something is not working",
            ),
        },
    )

    actions = plan_labels(specification, state)

    assert len(actions) == 1
    assert actions[0].operation == "drift"
    assert actions[0].description == ("Label 'bug' exists with drift: color differs")


def test_plan_labels_detects_description_drift() -> None:
    specification = ProjectSpecification(
        organization="org",
        repository="repo",
        project=Project(title="Project"),
        labels=[
            Label(
                name="bug",
                color="d73a4a",
                description="Expected description",
            ),
        ],
    )

    state = LabelState(
        labels={
            "bug": LabelSnapshot(
                name="bug",
                color="d73a4a",
                description="Current description",
            ),
        },
    )

    actions = plan_labels(specification, state)

    assert len(actions) == 1
    assert actions[0].operation == "drift"
    assert actions[0].description == (
        "Label 'bug' exists with drift: description differs"
    )
