"""Scenario export/import tests."""

from py_altium365.connection.json_con_search_async import FacedType

from test_interface.app.serializers import ScenarioDocument, SortFieldRow
from test_interface.app.session import HarnessSession


def test_scenario_round_trip(mocker):
    workspace = mocker.Mock()
    search = mocker.Mock()
    search.get_search_parameter.return_value = ["Component"]
    search.get_all_search_parameters.return_value = {"Manufacturer": ["Acme"]}
    search.get_all_search_parameters_range.return_value = {"Voltage": (1.0, 32.0, True, True)}
    search.get_search_parameter_wildcard.return_value = "cap"
    sort_field = mocker.Mock()
    sort_field.name = "HRID"
    sort_field.descending = False
    search.get_sort_fields.return_value = [sort_field]
    search.get_all_search_names_and_type.return_value = [("Manufacturer", FacedType.NO_TYPE)]
    search._search_counters = []
    workspace.create_search_object.return_value = search

    session = HarnessSession()
    session._api = mocker.Mock()
    session._workspace = workspace
    session._search = search

    exported = session.export_scenario()
    assert exported.content_types == ["Component"]
    assert exported.terms["Manufacturer"] == ["Acme"]

    session.import_scenario(
        ScenarioDocument(
            content_types=["Component"],
            terms={"Manufacturer": ["Other"]},
            ranges={},
            wildcard=None,
            sort_fields=[SortFieldRow(name="HRID", descending=True)],
        )
    )

    search.clear_search_parameters.assert_called()
    search.add_content_search_parameter.assert_called()


def test_api_scenarios(client, mocker):
    session = client.app.state.session
    search = mocker.Mock()
    search.get_search_parameter.return_value = []
    search.get_all_search_parameters.return_value = {}
    search.get_all_search_parameters_range.return_value = {}
    search.get_search_parameter_wildcard.return_value = None
    search.get_sort_fields.return_value = []
    session._api = mocker.Mock()
    session._workspace = mocker.Mock()
    session._search = search

    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert "content_types" in response.json()
