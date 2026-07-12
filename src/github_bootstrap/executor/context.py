"""Execution context."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionContext:
    """Shared execution context for resource executors."""

    owner_id: str
    repository_id: str
    owner: str
    repository: str
