"""Shared pytest fixtures for PyAltium365."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Generator, Tuple

import pytest
from requests import Response

from py_altium365.altium_api import AltiumApi

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: live Altium 365 tests (requires ALTIUM_USER and ALTIUM_PASS)",
    )


@pytest.fixture
def altium_credentials() -> Generator[Tuple[str, str], None, None]:
    user = os.environ.get("ALTIUM_USER")
    password = os.environ.get("ALTIUM_PASS")
    if not user or not password:
        pytest.skip("ALTIUM_USER and ALTIUM_PASS must be set for integration tests")
    yield user, password


@pytest.fixture
def mock_altium_api(mocker):
    api = mocker.Mock(spec=AltiumApi)
    api.login.return_value = True
    api.get_user_workspaces.return_value = []
    api.login_workspace.return_value = None
    api.get_service_url.return_value = None
    return api


@pytest.fixture
def mock_requests_session(mocker):
    """Injectable requests.Session mock for REST client unit tests."""
    return mocker.Mock()


@pytest.fixture
def components_list_response() -> Dict[str, Any]:
    with (FIXTURES_DIR / "components_list_response.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def _mock_json_response(payload: Dict[str, Any], status_code: int = 200) -> Response:
    response = Response()
    response.status_code = status_code
    response._content = json.dumps(payload).encode("utf-8")  # type: ignore[attr-defined]
    response.encoding = "utf-8"
    return response
