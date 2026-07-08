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


def test_missing_required_field() -> None:
    specification = {
        "repository": "repo",
        "project": {
            "title": "Project",
        },
    }

    try:
        validate_specification(specification)
    except SpecificationValidationError as error:
        assert str(error) == "Missing required field: organization"
    else:
        raise AssertionError("Expected validation error")
