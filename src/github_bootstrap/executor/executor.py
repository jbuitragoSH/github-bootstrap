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

        viewer = self.client.viewer()

        for action in plan.actions:
            if action.operation == "create" and action.resource == "project":
                self.client.create_project(
                    owner_id=viewer["id"],
                    title=action.payload["title"],
                )
