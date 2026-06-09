"""Shared fixtures for harness tests."""

import pytest
from fastapi.testclient import TestClient

from test_interface.app.main import create_app
from test_interface.app.session import HarnessSession


@pytest.fixture
def harness_session(mocker):
    mocker.patch("test_interface.app.session.ConnectionHandler.set_instance")
    api = mocker.Mock()
    session = HarnessSession(api_factory=lambda: api)
    session._test_api = api
    return session


@pytest.fixture
def mock_api(harness_session):
    return harness_session._test_api


@pytest.fixture
def client(harness_session, mock_api):
    app = create_app(session=harness_session)
    with TestClient(app) as test_client:
        yield test_client
