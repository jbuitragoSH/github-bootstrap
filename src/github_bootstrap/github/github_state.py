"""Aggregated GitHub state."""

from dataclasses import dataclass

from github_bootstrap.github.label_state import LabelState
from github_bootstrap.github.milestone_state import MilestoneState
from github_bootstrap.github.state import ProjectState


@dataclass(frozen=True)
class GitHubState:
    """Current GitHub state."""

    project: ProjectState
    labels: LabelState
    milestones: MilestoneState
