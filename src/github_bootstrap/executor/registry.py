"""Executor registry."""

from collections.abc import Callable

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.projects import execute_project_action
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.planner.actions import PlanAction

ExecutorFunction = Callable[
    [GitHubClient, ExecutionContext, PlanAction],
    None,
]

EXECUTORS: dict[str, ExecutorFunction] = {
    "project": execute_project_action,
}
