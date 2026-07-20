"""Plan GitHub issue synchronization."""

from github_bootstrap.github.issue_state import IssueState
from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.github.project_item_state import ProjectItemState
from github_bootstrap.planner.actions import PlanAction
from github_bootstrap.specification.models import ProjectSpecification


def plan_issues(
    specification: ProjectSpecification,
    issue_state: IssueState,
    milestone_state: MilestoneState,
    project_item_state: ProjectItemState,
) -> list[PlanAction]:
    """Generate actions required to synchronize issues with the project."""

    actions: list[PlanAction] = []

    milestones = {
        title.strip().lower(): snapshot
        for title, snapshot in milestone_state.milestones.items()
    }

    existing_issues = {
        snapshot.title.strip().lower(): snapshot
        for snapshot in issue_state.issues.values()
    }

    for issue in specification.issues:
        normalized_title = issue.title.strip().lower()

        existing_issue = existing_issues.get(normalized_title)

        # CASE 1:
        # Issue does not exist in repository -> create it.
        if existing_issue is None:
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
                        "fields": issue.fields,
                    },
                )
            )

            continue

        # CASE 2:
        # Issue exists. Synchronize its Project Item and fields.
        existing_project_item = project_item_state.items.get(
            existing_issue.id,
        )

        if existing_project_item is not None and not issue.fields:
            continue

        actions.append(
            PlanAction(
                operation="sync_project_item",
                resource="issue",
                description=f"Synchronize issue '{issue.title}' with project",
                payload={
                    "issue_id": existing_issue.id,
                    "project_item_id": (
                        existing_project_item.id
                        if existing_project_item is not None
                        else None
                    ),
                    "fields": issue.fields,
                },
            )
        )

    return actions
