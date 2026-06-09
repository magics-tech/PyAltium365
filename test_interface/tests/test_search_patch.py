"""Search patch pure logic tests."""

import pytest

from py_altium365.connection.json_con_search_async import FacedType, JsonFacetedCounter

from test_interface.app.search_patch import PatchError, SearchPatch, apply_patch, validate_patch


def test_validate_unknown_facet(mocker):
    search = mocker.Mock()
    search.get_all_search_names_and_type.return_value = []
    search._search_counters = []

    with pytest.raises(PatchError, match="Unknown facet"):
        validate_patch(search, SearchPatch(action="add_term", facet_name="Voltage", value="5V"))


def test_apply_content_types(mocker):
    search = mocker.Mock()
    search.get_all_search_names_and_type.return_value = []

    apply_patch(search, SearchPatch(action="set_content_types", content_types=["Component"], remove_old=True))

    search.add_content_search_parameter.assert_called_once()


def test_apply_range_requires_support(mocker):
    search = mocker.Mock()
    search.get_all_search_names_and_type.return_value = [("Voltage", FacedType.VOLTAGE)]
    search._search_counters = [
        JsonFacetedCounter(FacetName="Voltage", faced_type=FacedType.VOLTAGE, TotalHitCount=0, Counters=[], SupportRange=False)
    ]

    with pytest.raises(PatchError, match="does not support range"):
        apply_patch(
            search,
            SearchPatch(action="set_range", facet_name="Voltage", min_value=1.0, max_value=5.0, faced_type=FacedType.VOLTAGE.value),
        )
