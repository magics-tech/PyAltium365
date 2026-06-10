"""Components REST API client unit tests."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from py_altium365.base.field_encoding import COMPONENTS_API_FIELD_SUFFIX
from py_altium365.connection.components.components_api import (
    ComponentRecord,
    ComponentsApiClient,
    ComponentsListPage,
    ComponentsQuery,
)


def _json_response(payload, status_code=200):
    from requests import Response

    response = Response()
    response.status_code = status_code
    response._content = json.dumps(payload).encode("utf-8")  # type: ignore[attr-defined]
    response.encoding = "utf-8"
    return response


def _make_client(mock_requests_session, mocker, base_url="https://ws.example/components/api/components"):
    return ComponentsApiClient(
        mock_requests_session,
        base_url,
        "session-guid-123",
    )


def test_components_query_to_params():
    query = ComponentsQuery(
        fields=["Id", "HRID", "Update Date"],
        order_by=[("Update Date", True)],
        start=10,
        limit=25,
        text="cap",
        tag="",
    )
    params = query.to_params(field_suffix=COMPONENTS_API_FIELD_SUFFIX)

    assert params["start"] == 10
    assert params["limit"] == 25
    assert params["text"] == "cap"
    assert params["fields[]"] == ["Id", "HRID", "Update Date"]
    assert params["orderby[]"] == [f"-Update_20Date{COMPONENTS_API_FIELD_SUFFIX}"]


def test_list_page_builds_request(mock_requests_session, components_list_response, mocker):
    mock_requests_session.get.return_value = _json_response(components_list_response)
    client = _make_client(mock_requests_session, mocker)

    page = client.list_page(limit=50)

    mock_requests_session.get.assert_called_once()
    call_kwargs = mock_requests_session.get.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "AFSSessionID session-guid-123"
    assert call_kwargs["headers"]["User-Agent"] == "Altium Designer"
    assert "host" not in call_kwargs["headers"]
    assert call_kwargs["params"]["limit"] == 50
    assert "fields[]" in call_kwargs["params"]
    assert "orderby[]" in call_kwargs["params"]
    assert page.total == 2
    assert len(page.items) == 2
    assert page.items[0].hrid == "CMP-001"


def test_parse_fixture_into_component_record(components_list_response):
    page = ComponentsListPage.from_response(components_list_response)
    record = page.items[0]
    assert isinstance(record, ComponentRecord)
    assert record.item_guid == "A1B2C3D4-E5F6-7890-ABCD-EF1234567890"
    assert record.update_date == datetime.fromisoformat("2026-06-02T14:30:00")
    assert record.revision_state == "Draft"


def test_find_by_hrid(mock_requests_session, components_list_response, mocker):
    mock_requests_session.get.return_value = _json_response(components_list_response)
    client = _make_client(mock_requests_session, mocker)

    found = client.find_by_hrid("CMP-002")
    assert found is not None
    assert found.hrid == "CMP-002"
    assert client.find_by_hrid("MISSING") is None


def test_list_recent_stops_at_watermark(mock_requests_session, mocker):
    payload = {
        "Total": 2,
        "Items": [
            {
                "Id": 1,
                "ItemGUID": "guid-recent",
                "HRID": "CMP-RECENT",
                "Update Date": "2026-06-02T12:00:00",
                "Description": "",
                "Comment": "",
                "Revision State": "Draft",
            },
            {
                "Id": 2,
                "ItemGUID": "guid-old",
                "HRID": "CMP-OLD",
                "Update Date": "2026-05-01T12:00:00",
                "Description": "",
                "Comment": "",
                "Revision State": "Draft",
            },
        ],
    }
    mock_requests_session.get.return_value = _json_response(payload)
    client = _make_client(mock_requests_session, mocker)

    since = datetime(2026, 6, 1, 12, 0, 0)
    results = client.list_recent(since)

    assert len(results) == 1
    assert results[0].hrid == "CMP-RECENT"


def test_create_components_client_on_workspace(mocker):
    from py_altium365.altium_api_workspace import AltiumApiWorkspace

    workspace_url = "https://ws.example"
    service_discovery = mocker.Mock()
    service_discovery.user_info.session_id = "sess-1"
    service_discovery.service_urls.SEARCHBASE = "https://search"
    service_discovery.service_urls.Library_Components_Api = None

    mocker.patch("py_altium365.altium_api_workspace.ConnectionHandler.get_instance", return_value=mocker.Mock())
    workspace = AltiumApiWorkspace(workspace_url, service_discovery)
    client = workspace.create_components_client()

    assert isinstance(client, ComponentsApiClient)
    assert client._url == "https://ws.example/components/api/components"  # pylint: disable=protected-access


def test_create_components_client_uses_workspace_components_path(mocker):
    from py_altium365.altium_api_workspace import AltiumApiWorkspace

    workspace_url = "https://magics-instruments-nv.365.altium.com:443"
    service_discovery = mocker.Mock()
    service_discovery.user_info.session_id = "sess-1"
    service_discovery.service_urls.SEARCHBASE = "https://search"
    service_discovery.service_urls.Library_Components_Api = (
        "https://eur.365.altium.com/librarycomponentsapi/api"
    )

    mocker.patch("py_altium365.altium_api_workspace.ConnectionHandler.get_instance", return_value=mocker.Mock())
    workspace = AltiumApiWorkspace(workspace_url, service_discovery)
    client = workspace.create_components_client()

    assert client._url == "https://magics-instruments-nv.365.altium.com/components/api/components"  # pylint: disable=protected-access
