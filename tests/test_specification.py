import pytest

from github_bootstrap.specification.validator import (
    SpecificationValidationError,
    validate_specification,
)


def test_valid_specification_with_fields() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "name": "Component",
                "type": "text",
            },
            {
                "name": "Story Points",
                "type": "number",
            },
            {
                "name": "Due Date",
                "type": "date",
            },
            {
                "name": "Priority",
                "type": "single_select",
                "options": [
                    "Low",
                    "Medium",
                    "High",
                ],
            },
            {
                "name": "Sprint",
                "type": "iteration",
            },
        ],
    }

    result = validate_specification(specification)

    assert result == specification


def test_fields_must_be_a_list() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": {
            "name": "Component",
            "type": "text",
        },
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Field 'fields' must be a list\.",
    ):
        validate_specification(specification)


def test_field_must_be_a_mapping() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            "Component",
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Field 'fields\[0\]' must be a mapping\.",
    ):
        validate_specification(specification)


def test_field_requires_name() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "type": "text",
            },
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Missing required field: fields\[0\]\.name",
    ):
        validate_specification(specification)


def test_field_requires_type() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "name": "Component",
            },
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Missing required field: fields\[0\]\.type",
    ):
        validate_specification(specification)


def test_field_type_must_be_supported() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "name": "Component",
                "type": "unsupported",
            },
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Unsupported field type: fields\[0\]\.type='unsupported'",
    ):
        validate_specification(specification)


def test_single_select_options_must_be_a_list() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "name": "Priority",
                "type": "single_select",
                "options": "Low",
            },
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=r"Field 'fields\[0\]\.options' must be a list\.",
    ):
        validate_specification(specification)


def test_single_select_options_must_be_strings() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "fields": [
            {
                "name": "Priority",
                "type": "single_select",
                "options": [
                    "Low",
                    2,
                ],
            },
        ],
    }

    with pytest.raises(
        SpecificationValidationError,
        match=(
            r"Field 'fields\[0\]\.options\[1\]' "
            r"must be a string\."
        ),
    ):
        validate_specification(specification)
