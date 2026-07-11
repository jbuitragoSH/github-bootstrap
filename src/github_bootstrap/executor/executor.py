"""Execute synchronization plans."""

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
    ) -> None:
        """Execute the synchronization plan."""

        for action in plan.actions:
            print(action.description)
