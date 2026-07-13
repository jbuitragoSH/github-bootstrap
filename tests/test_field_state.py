from github_bootstrap.github.field_state import FieldState


def test_field_state_contains_existing_fields() -> None:
    state = FieldState(
        fields={
            "Title",
            "Status",
            "Priority",
        },
    )

    assert state.fields == {
        "Title",
        "Status",
        "Priority",
    }


def test_field_state_can_be_empty() -> None:
    state = FieldState(
        fields=set(),
    )

    assert state.fields == set()
