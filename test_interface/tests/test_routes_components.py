"""Components route tests."""

from datetime import datetime

from py_altium365.connection.components.components_api import ComponentRecord, ComponentsListPage


def _connected_workspace(client, mock_api, mocker):
    mock_api.get_user_workspaces.return_value = []
    session = client.app.state.session
    workspace = mocker.Mock()
    workspace.workspace_url = "https://ws.example"
    components_client = mocker.Mock()
    workspace.create_components_client.return_value = components_client
    session._api = mock_api
    session._workspace = workspace
    session._credentials = ("u", "p")
    session._components_client = components_client
    return components_client


def test_components_meta(client, mock_api, mocker):
    _connected_workspace(client, mock_api, mocker)
    response = client.get("/api/components/meta")
    assert response.status_code == 200
    body = response.json()
    assert "HRID" in body["field_options"]
    assert body["query"]["limit"] == 50


def test_components_query_patch(client, mock_api, mocker):
    _connected_workspace(client, mock_api, mocker)
    response = client.post("/api/components/query", json={"action": "set_text", "text": "resistor"})
    assert response.status_code == 200
    assert response.json()["query"]["text"] == "resistor"


def test_components_results(client, mock_api, mocker):
    components_client = _connected_workspace(client, mock_api, mocker)
    components_client.list_page.return_value = ComponentsListPage(
        total=1,
        items=[
            ComponentRecord(
                item_guid="guid-1",
                hrid="CMP-001",
                update_date=datetime(2026, 6, 1),
                revision_state="Draft",
            )
        ],
    )
    response = client.get("/api/components/results")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["hrid"] == "CMP-001"


def test_find_hrid(client, mock_api, mocker):
    components_client = _connected_workspace(client, mock_api, mocker)
    components_client.find_by_hrid.return_value = ComponentRecord(item_guid="g", hrid="CMP-99")
    response = client.get("/api/components/find-hrid", params={"hrid": "CMP-99"})
    assert response.status_code == 200
    assert response.json()["found"] is True
