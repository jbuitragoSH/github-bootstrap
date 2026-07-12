import pytest

from github_bootstrap.specification.validator import (
    SpecificationValidationError,
    validate_specification,
)


def test_valid_specification() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
    }

    validate_specification(specification)


def test_valid_specification_with_milestones() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "milestones": [
            {
                "title": "Sprint 1",
                "description": "Foundation capabilities",
                "due_on": "2026-07-31",
            },
            {
                "title": "Sprint 2",
            },
        ],
    }

    result = validate_specification(specification)

    assert result == specification


def test_missing_required_field() -> None:
    specification = {
        "repository": "repo",
        "project": {
            "title": "Project",
        },
    }

    with pytest.raises(
        SpecificationValidationError,
        match="Missing required field: organization",
    ):
        validate_specification(specification)


def test_milestones_must_be_a_list() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "milestones": {
            "title": "Sprint 1",
        },
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Field 'milestones' must be a list\.",
    ):
        validate_specification(specification)


def test_milestone_must_be_a_mapping() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "milestones": [
            "Sprint 1",
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Field 'milestones\[0\]' must be a mapping\.",
    ):
        validate_specification(specification)


def test_milestone_requires_title() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "milestones": [
            {
                "description": "Foundation capabilities",
            },
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Missing required field: milestones\[0\]\.title",
    ):
        validate_specification(specification)
