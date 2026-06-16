"""RestListClient parametrized URL-building tests."""

import json

import httpx
import pytest

from py_altium365.base.field_encoding import COMPONENTS_API_FIELD_SUFFIX
from py_altium365.connection.components.components_api import ComponentsApiClient, ComponentsQuery


def _json_response(payload, status_code=200):
    return httpx.Response(
        status_code=status_code,
        content=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
    )


@pytest.mark.anyio
async def test_rest_list_client_builds_orderby_params(mocker):
    mock_client = mocker.AsyncMock()
    mock_client.get = mocker.AsyncMock(return_value=_json_response({"Total": 0, "Items": []}))
    client = ComponentsApiClient(
        mock_client,
        "https://ws.example/components/api/components",
        "sess",
    )
    query = ComponentsQuery(fields=["HRID"], order_by=[("Update Date", True)], limit=10)
    await client.list_page(query)

    params = mock_client.get.call_args.kwargs["params"]
    assert params["fields[]"] == ["HRID"]
    assert params["orderby[]"] == [f"-Update_20Date{COMPONENTS_API_FIELD_SUFFIX}"]
