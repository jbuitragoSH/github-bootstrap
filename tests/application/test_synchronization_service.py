from unittest.mock import Mock

from pytest import MonkeyPatch

from github_bootstrap.application.synchronization_service import (
    SynchronizationService,
)
from github_bootstrap.github.project_item_state import ProjectItemState
from github_bootstrap.planner.plan import Plan
from github_bootstrap.specification.models import ProjectSpecification


def test_dry_run_builds_plan_without_executing(
    monkeypatch: MonkeyPatch,
) -> None:
    client = Mock()
    service = SynchronizationService(client)

    specification = Mock(spec=ProjectSpecification)
    github_state = Mock()
    expected_plan = Plan()

    load_state = Mock(return_value=github_state)
    create_plan = Mock(return_value=expected_plan)
    execute = Mock()

    monkeypatch.setattr(
        service,
        "_load_github_state",
        load_state,
    )

    monkeypatch.setattr(
        "github_bootstrap.application.synchronization_service.create_plan",
        create_plan,
    )

    monkeypatch.setattr(
        service._executor,
        "execute",
        execute,
    )

    result = service.dry_run(specification)

    assert result.plan is expected_plan

    load_state.assert_called_once_with(specification)

    create_plan.assert_called_once_with(
        specification,
        github_state,
    )

    execute.assert_not_called()


def test_synchronize_executes_phases_in_order(
    monkeypatch: MonkeyPatch,
) -> None:
    client = Mock()

    client.viewer.return_value = {
        "id": "owner-id",
    }

    repository = Mock()
    repository.id = "repository-id"

    client.repositories.find.return_value = repository

    service = SynchronizationService(client)

    specification = Mock(spec=ProjectSpecification)
    specification.organization = "example-org"
    specification.repository = "example-repository"

    initial_state = Mock()
    project_state = Mock()
    infrastructure_state = Mock()

    states = [
        initial_state,
        project_state,
        infrastructure_state,
    ]

    load_state = Mock(side_effect=states)

    complete_plan = Mock(spec=Plan)
    complete_plan.executable_actions.return_value = [
        Mock(),
    ]

    project_plan = Plan()
    infrastructure_plan = Plan()
    issue_plan = Plan()

    create_plan = Mock(return_value=complete_plan)
    create_project_plan = Mock(return_value=project_plan)
    create_infrastructure_plan = Mock(
        return_value=infrastructure_plan,
    )
    create_issue_plan = Mock(return_value=issue_plan)

    execute = Mock()

    monkeypatch.setattr(
        service,
        "_load_github_state",
        load_state,
    )

    monkeypatch.setattr(
        "github_bootstrap.application.synchronization_service.create_plan",
        create_plan,
    )

    monkeypatch.setattr(
        "github_bootstrap.application.synchronization_service.create_project_plan",
        create_project_plan,
    )

    monkeypatch.setattr(
        "github_bootstrap.application.synchronization_service.create_infrastructure_plan",
        create_infrastructure_plan,
    )

    monkeypatch.setattr(
        "github_bootstrap.application.synchronization_service.create_issue_plan",
        create_issue_plan,
    )

    monkeypatch.setattr(
        service._executor,
        "execute",
        execute,
    )

    monkeypatch.setattr(
        service,
        "_create_execution_context",
        Mock(
            side_effect=[
                Mock(),
                Mock(),
                Mock(),
            ]
        ),
    )

    result = service.synchronize(specification)

    assert result.plan is complete_plan

    assert load_state.call_count == 3

    create_plan.assert_called_once_with(
        specification,
        initial_state,
    )

    create_project_plan.assert_called_once_with(
        specification,
        initial_state,
    )

    create_infrastructure_plan.assert_called_once_with(
        specification,
        project_state,
    )

    create_issue_plan.assert_called_once_with(
        specification,
        infrastructure_state,
    )

    assert execute.call_count == 3

    assert execute.call_args_list[0].args[0] is project_plan
    assert execute.call_args_list[1].args[0] is infrastructure_plan
    assert execute.call_args_list[2].args[0] is issue_plan


def test_synchronize_skips_execution_when_plan_has_no_actions(
    monkeypatch: MonkeyPatch,
) -> None:
    client = Mock()
    service = SynchronizationService(client)

    specification = Mock(spec=ProjectSpecification)
    github_state = Mock()

    complete_plan = Mock(spec=Plan)
    complete_plan.executable_actions.return_value = []

    load_state = Mock(return_value=github_state)
    create_plan = Mock(return_value=complete_plan)
    execute = Mock()

    monkeypatch.setattr(
        service,
        "_load_github_state",
        load_state,
    )

    monkeypatch.setattr(
        "github_bootstrap.application.synchronization_service.create_plan",
        create_plan,
    )

    monkeypatch.setattr(
        service._executor,
        "execute",
        execute,
    )

    result = service.synchronize(specification)

    assert result.plan is complete_plan

    load_state.assert_called_once_with(specification)
    execute.assert_not_called()


def test_load_github_state_uses_empty_project_items_without_project_id(
    monkeypatch: MonkeyPatch,
) -> None:
    client = Mock()

    project_state = Mock()
    project_state.id = None

    client.projects.find.return_value = project_state
    client.labels.find.return_value = Mock()
    client.milestones.find.return_value = Mock()
    client.fields.find.return_value = Mock()
    client.issues.find.return_value = Mock()

    service = SynchronizationService(client)

    specification = Mock(spec=ProjectSpecification)
    specification.organization = "example-org"
    specification.repository = "example-repository"

    specification.project = Mock()
    specification.project.title = "Example Development"

    state = service._load_github_state(specification)

    assert isinstance(
        state.project_items,
        ProjectItemState,
    )

    assert state.project_items.items == {}

    client.project_items.find.assert_not_called()
