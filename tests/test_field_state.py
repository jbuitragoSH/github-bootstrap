from github_bootstrap.github.field_state import (
    FieldOptionSnapshot,
    FieldSnapshot,
    FieldState,
)


def test_field_state_contains_existing_fields() -> None:
    state = FieldState(
        fields={
            "Status": FieldSnapshot(
                id="field-status",
                name="Status",
                data_type="SINGLE_SELECT",
                options=(
                    FieldOptionSnapshot(
                        id="option-todo",
                        name="Todo",
                    ),
                    FieldOptionSnapshot(
                        id="option-done",
                        name="Done",
                    ),
                ),
            ),
            "Priority": FieldSnapshot(
                id="field-priority",
                name="Priority",
                data_type="SINGLE_SELECT",
                options=(
                    FieldOptionSnapshot(
                        id="option-low",
                        name="Low",
                    ),
                    FieldOptionSnapshot(
                        id="option-medium",
                        name="Medium",
                    ),
                    FieldOptionSnapshot(
                        id="option-high",
                        name="High",
                    ),
                ),
            ),
        },
    )

    assert state.fields["Status"].id == "field-status"
    assert state.fields["Status"].name == "Status"
    assert state.fields["Status"].data_type == "SINGLE_SELECT"

    assert tuple(option.name for option in state.fields["Status"].options) == (
        "Todo",
        "Done",
    )


def test_field_state_can_be_empty() -> None:
    state = FieldState(
        fields={},
    )

    assert state.fields == {}
