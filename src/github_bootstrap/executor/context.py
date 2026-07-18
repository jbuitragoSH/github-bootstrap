from dataclasses import dataclass

from github_bootstrap.github.field_state import FieldState


@dataclass(frozen=True)
class ExecutionContext:
    """Shared execution context for resource executors."""

    owner_id: str
    repository_id: str
    owner: str
    repository: str
    project_id: str | None = None
    field_state: FieldState | None = None
