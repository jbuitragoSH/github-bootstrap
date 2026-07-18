"""Executor registry."""

from collections.abc import Callable

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.fields import execute_field_action
from github_bootstrap.executor.issues import execute_issue_action
from github_bootstrap.executor.labels import execute_label_action
from github_bootstrap.executor.milestones import execute_milestone_action
from github_bootstrap.executor.projects import execute_project_action
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.planner.actions import PlanAction

ExecutorFunction = Callable[
    [GitHubClient, ExecutionContext, PlanAction],
    None,
]

EXECUTORS: dict[str, ExecutorFunction] = {
    "project": execute_project_action,
    "label": execute_label_action,
    "milestone": execute_milestone_action,
    "field": execute_field_action,
    "issue": execute_issue_action,
}
