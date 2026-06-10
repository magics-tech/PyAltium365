"""RestListClient parametrized URL-building tests."""

import json

from py_altium365.base.field_encoding import COMPONENTS_API_FIELD_SUFFIX
from py_altium365.connection.components.components_api import ComponentsApiClient, ComponentsQuery


def _json_response(payload, status_code=200):
    from requests import Response

    response = Response()
    response.status_code = status_code
    response._content = json.dumps(payload).encode("utf-8")  # type: ignore[attr-defined]
    response.encoding = "utf-8"
    return response


def test_rest_list_client_builds_orderby_params(mock_requests_session):
    mock_requests_session.get.return_value = _json_response({"Total": 0, "Items": []})
    client = ComponentsApiClient(
        mock_requests_session,
        "https://ws.example/components/api/components",
        "sess",
    )
    query = ComponentsQuery(fields=["HRID"], order_by=[("Update Date", True)], limit=10)
    client.list_page(query)

    params = mock_requests_session.get.call_args.kwargs["params"]
    assert params["fields[]"] == ["HRID"]
    assert params["orderby[]"] == [f"-Update_20Date{COMPONENTS_API_FIELD_SUFFIX}"]
