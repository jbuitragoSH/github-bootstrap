"""Specification models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    """GitHub Project configuration."""

    title: str


@dataclass(frozen=True)
class ProjectSpecification:
    """Root project specification."""

    organization: str
    repository: str
    project: Project
