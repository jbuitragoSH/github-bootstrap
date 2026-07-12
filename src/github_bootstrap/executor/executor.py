"""Execute synchronization plans."""

from github_bootstrap.executor.context import ExecutionContext
from github_bootstrap.executor.registry import EXECUTORS
from github_bootstrap.github.client import GitHubClient
from github_bootstrap.planner.plan import Plan


class Executor:
    """Execute synchronization plans."""

    def __init__(
        self,
        client: GitHubClient,
    ) -> None:
        self.client = client

    def execute(
        self,
        plan: Plan,
        context: ExecutionContext,
    ) -> None:
        """Execute the synchronization plan."""

        for action in plan.actions:
            executor = EXECUTORS.get(action.resource)

            if executor is None:
                continue

            executor(
                self.client,
                context,
                action,
            )
