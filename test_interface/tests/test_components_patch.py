"""Components patch unit tests."""

from py_altium365.connection.components.components_api import ComponentsQuery

from test_interface.app.components_patch import ComponentsPatch, OrderByPatch, PatchError, apply_patch, default_components_query


def test_default_query_has_update_date_desc():
    query = default_components_query()
    assert query.order_by == [("Update Date", True)]
    assert "HRID" in query.fields


def test_apply_set_text_patch():
    base = default_components_query()
    updated = apply_patch(base, ComponentsPatch(action="set_text", text="capacitor"))
    assert updated.text == "capacitor"


def test_apply_set_order_by_encodes_via_query():
    base = default_components_query()
    updated = apply_patch(
        base,
        ComponentsPatch(
            action="set_order_by",
            order_by=[OrderByPatch(name="Update Date", descending=True)],
        ),
    )
    params = updated.to_params()
    assert any("Update_20Date" in value for value in params["orderby[]"])


def test_apply_set_query_round_trip():
    saved = ComponentsQuery(text="CMP-001", limit=10)
    result = apply_patch(default_components_query(), ComponentsPatch(action="set_query", query=saved))
    assert result.text == "CMP-001"
    assert result.limit == 10


def test_validate_patch_requires_fields():
    try:
        apply_patch(default_components_query(), ComponentsPatch(action="set_fields", fields=[]))
        raised = False
    except PatchError:
        raised = True
    assert raised
