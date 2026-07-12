from github_bootstrap.specification.parser import parse_specification


def test_parse_specification_with_labels() -> None:
    specification = {
        "organization": "org",
        "repository": "repo",
        "project": {
            "title": "Project",
        },
        "labels": [
            {
                "name": "bug",
                "color": "d73a4a",
                "description": "Bug report",
            },
            {
                "name": "documentation",
                "color": "0075ca",
            },
        ],
    }

    result = parse_specification(specification)

    assert result.organization == "org"
    assert result.repository == "repo"
    assert result.project.title == "Project"

    assert len(result.labels) == 2

    assert result.labels[0].name == "bug"
    assert result.labels[0].color == "d73a4a"
    assert result.labels[0].description == "Bug report"

    assert result.labels[1].name == "documentation"
    assert result.labels[1].color == "0075ca"
    assert result.labels[1].description is None
