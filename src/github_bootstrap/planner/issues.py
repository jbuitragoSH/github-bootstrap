"""Plan GitHub issue synchronization."""

from github_bootstrap.github.issue_state import IssueState
from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import ProjectSpecification


def plan_issues(
    specification: ProjectSpecification,
    issue_state: IssueState,
    milestone_state: MilestoneState,
) -> list[PlanAction]:
    """Generate actions required to create missing issues."""

    actions: list[PlanAction] = []

    existing_titles = set(issue_state.issues)

    milestones = {
        title.strip().lower(): snapshot
        for title, snapshot in milestone_state.milestones.items()
    }

    for issue in specification.issues:
        normalized_title = issue.title.strip().lower()

        if normalized_title in existing_titles:
            continue

        milestone_number = None

        if issue.milestone is not None:
            milestone = milestones.get(
                issue.milestone.strip().lower(),
            )

            if milestone is not None:
                milestone_number = milestone.number

        actions.append(
            PlanAction(
                operation="create",
                resource="issue",
                description=f"Create issue '{issue.title}'",
                payload={
                    "title": issue.title,
                    "body": issue.body,
                    "labels": issue.labels,
                    "milestone": milestone_number,
                },
            )
        )

    return actions
