from github_bootstrap.github.field_state import FieldSnapshot, FieldState


def test_field_state_contains_existing_fields() -> None:
    state = FieldState(
        fields={
            "Status": FieldSnapshot(
                name="Status",
                data_type="SINGLE_SELECT",
                options=("Todo", "Done"),
            ),
            "Priority": FieldSnapshot(
                name="Priority",
                data_type="SINGLE_SELECT",
                options=("Low", "Medium", "High"),
            ),
        },
    )

    assert state.fields["Status"].name == "Status"
    assert state.fields["Status"].data_type == "SINGLE_SELECT"
    assert state.fields["Status"].options == ("Todo", "Done")


def test_field_state_can_be_empty() -> None:
    state = FieldState(
        fields={},
    )

    assert state.fields == {}
