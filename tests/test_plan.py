from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.planner.plan import Plan


def test_plan_returns_drift_actions() -> None:
    plan = Plan(
        actions=[
            PlanAction(
                operation="create",
                resource="field",
                description="Create field",
                payload={
                    "name": "Priority",
                },
            ),
            PlanAction(
                operation="drift",
                resource="field",
                description="Field 'Priority' exists with drift",
                payload={
                    "name": "Priority",
                    "reason": "options differ",
                },
            ),
        ],
    )

    drift_actions = plan.drift_actions()

    assert len(drift_actions) == 1
    assert drift_actions[0].operation == "drift"
    assert drift_actions[0].payload == {
        "name": "Priority",
        "reason": "options differ",
    }


def test_plan_returns_executable_actions() -> None:
    plan = Plan(
        actions=[
            PlanAction(
                operation="create",
                resource="field",
                description="Create field",
                payload={
                    "name": "Priority",
                },
            ),
            PlanAction(
                operation="drift",
                resource="field",
                description="Field 'Priority' exists with drift",
                payload={
                    "name": "Priority",
                    "reason": "options differ",
                },
            ),
        ],
    )

    executable_actions = plan.executable_actions()

    assert len(executable_actions) == 1
    assert executable_actions[0].operation == "create"


def test_plan_detects_drift() -> None:
    plan = Plan(
        actions=[
            PlanAction(
                operation="drift",
                resource="field",
                description="Field 'Priority' exists with drift",
                payload={
                    "name": "Priority",
                    "reason": "options differ",
                },
            ),
        ],
    )

    assert plan.has_drift() is True


def test_plan_without_drift_returns_false() -> None:
    plan = Plan(
        actions=[
            PlanAction(
                operation="create",
                resource="field",
                description="Create field",
                payload={
                    "name": "Priority",
                },
            ),
        ],
    )

    assert plan.has_drift() is False


def test_plan_returns_executable_actions_without_drift() -> None:
    plan = Plan(
        actions=[
            PlanAction(
                operation="create",
                resource="field",
                description="Create field",
                payload={
                    "name": "Priority",
                },
            ),
            PlanAction(
                operation="drift",
                resource="field",
                description="Field 'Priority' exists with drift",
                payload={
                    "name": "Priority",
                    "reason": "options differ",
                },
            ),
        ],
    )

    executable_actions = plan.executable_actions()

    assert len(executable_actions) == 1
    assert executable_actions[0].operation == "create"
