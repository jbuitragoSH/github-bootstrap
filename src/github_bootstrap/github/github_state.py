"""Aggregated GitHub state."""

from dataclasses import dataclass

from github_bootstrap.github.field_state import FieldState
from github_bootstrap.github.issue_state import IssueState
from github_bootstrap.github.label_state import LabelState
from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.github.project_item_state import ProjectItemState
from github_bootstrap.github.state import ProjectState


@dataclass(frozen=True)
class GitHubState:
    """Current GitHub state."""

    project: ProjectState
    labels: LabelState
    milestones: MilestoneState
    fields: FieldState
    issues: IssueState
    project_items: ProjectItemState
