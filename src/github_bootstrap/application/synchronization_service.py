"""Application service for GitHub synchronization."""

from dataclasses import dataclass

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.executor import Executor
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.github.github_state import GitHubState
from github_bootstrap.github.project_item_state import ProjectItemState
from github_bootstrap.planner.plan import (
    Plan,
    create_infrastructure_plan,
    create_issue_plan,
    create_plan,
    create_project_plan,
)
from github_bootstrap.specification.models import ProjectSpecification


@dataclass(frozen=True)
class SynchronizationResult:
    """Result produced by a synchronization operation."""

    plan: Plan


class SynchronizationService:
    """Coordinate GitHub project synchronization."""

    def __init__(self, client: GitHubClient) -> None:
        self._client = client
        self._executor = Executor(client)

    def dry_run(
        self,
        specification: ProjectSpecification,
    ) -> SynchronizationResult:
        """Build the synchronization plan without applying changes."""

        github_state = self._load_github_state(specification)

        plan = create_plan(
            specification,
            github_state,
        )

        return SynchronizationResult(plan=plan)

    def synchronize(
        self,
        specification: ProjectSpecification,
    ) -> SynchronizationResult:
        """Synchronize the configured GitHub environment."""

        github_state = self._load_github_state(specification)

        complete_plan = create_plan(
            specification,
            github_state,
        )

        if not complete_plan.executable_actions():
            return SynchronizationResult(plan=complete_plan)

        viewer = self._client.viewer()

        repository = self._client.repositories.find(
            owner=specification.organization,
            repository=specification.repository,
        )

        # Phase 1: create the Project V2.
        project_plan = create_project_plan(
            specification,
            github_state,
        )

        self._executor.execute(
            project_plan,
            self._create_execution_context(
                specification=specification,
                github_state=github_state,
                owner_id=viewer["id"],
                repository_id=repository.id,
            ),
        )

        # Reload state so the new Project ID is available.
        github_state = self._load_github_state(specification)

        # Phase 2: create labels, milestones, and fields.
        infrastructure_plan = create_infrastructure_plan(
            specification,
            github_state,
        )

        self._executor.execute(
            infrastructure_plan,
            self._create_execution_context(
                specification=specification,
                github_state=github_state,
                owner_id=viewer["id"],
                repository_id=repository.id,
            ),
        )

        # Reload state so milestone numbers, field IDs,
        # option IDs, and iteration IDs are available.
        github_state = self._load_github_state(specification)

        # Phase 3: create or synchronize issues.
        issue_plan = create_issue_plan(
            specification,
            github_state,
        )

        self._executor.execute(
            issue_plan,
            self._create_execution_context(
                specification=specification,
                github_state=github_state,
                owner_id=viewer["id"],
                repository_id=repository.id,
            ),
        )

        return SynchronizationResult(plan=complete_plan)

    def _load_github_state(
        self,
        specification: ProjectSpecification,
    ) -> GitHubState:
        """Load the current GitHub synchronization state."""

        project_state = self._client.projects.find(
            specification.project.title,
        )

        label_state = self._client.labels.find(
            owner=specification.organization,
            repository=specification.repository,
        )

        milestone_state = self._client.milestones.find(
            owner=specification.organization,
            repository=specification.repository,
        )

        field_state = self._client.fields.find(
            project_title=specification.project.title,
        )

        issue_state = self._client.issues.find(
            owner=specification.organization,
            repository=specification.repository,
        )

        if project_state.id is not None:
            project_item_state = self._client.project_items.find(
                project_id=project_state.id,
            )
        else:
            project_item_state = ProjectItemState(
                items={},
            )

        return GitHubState(
            project=project_state,
            labels=label_state,
            milestones=milestone_state,
            fields=field_state,
            issues=issue_state,
            project_items=project_item_state,
        )

    @staticmethod
    def _create_execution_context(
        specification: ProjectSpecification,
        github_state: GitHubState,
        owner_id: str,
        repository_id: str,
    ) -> ExecutionContext:
        """Create an execution context for the current synchronization phase."""

        return ExecutionContext(
            owner_id=owner_id,
            repository_id=repository_id,
            owner=specification.organization,
            repository=specification.repository,
            project_id=github_state.project.id,
            field_state=github_state.fields,
        )
