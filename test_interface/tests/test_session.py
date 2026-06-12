"""HarnessSession unit tests."""

import pytest

from test_interface.app.search_patch import SearchPatch
from test_interface.app.session import HarnessSession


def test_login_success(mocker):
    api = mocker.Mock()
    api.login.return_value = True
    api.get_user_workspaces.return_value = [mocker.Mock(), mocker.Mock()]
    session = HarnessSession(api_factory=lambda: api)

    result = session.login("user", "pass")

    assert result.success is True
    assert result.workspace_count == 2
    assert session.api is api


def test_login_failure(mocker):
    api = mocker.Mock()
    api.login.return_value = "Bad credentials"
    session = HarnessSession(api_factory=lambda: api)

    result = session.login("user", "pass")

    assert result.success is False
    assert result.message == "Bad credentials"
    assert session.api is None


def test_login_connection_error(mocker):
    api = mocker.Mock()
    api.login.side_effect = ConnectionError("network down")
    session = HarnessSession(api_factory=lambda: api)

    result = session.login("user", "pass")

    assert result.success is False
    assert "network down" in result.message


def test_logout_clears_state(mocker):
    api = mocker.Mock()
    api.login.return_value = True
    api.get_user_workspaces.return_value = []
    session = HarnessSession(api_factory=lambda: api)
    session.login("user", "pass")

    session.logout()

    assert session.api is None
    assert session.workspace is None
    assert session.search is None


def test_connect_workspace_by_url(mocker):
    api = mocker.Mock()
    ws = mocker.Mock()
    ws.workspace_id = 1
    ws.hosting_url = "https://ws.example"
    ws.name = "Main"
    api.get_user_workspaces.return_value = [ws]
    workspace = mocker.Mock()
    api.login_workspace.return_value = workspace

    session = HarnessSession(api_factory=lambda: api)
    session._api = api
    session._credentials = ("user", "pass")

    assert session.connect_workspace("https://ws.example") is True
    assert session.workspace is workspace


def test_connect_workspace_requires_portal():
    session = HarnessSession()
    with pytest.raises(PermissionError):
        session.connect_workspace("https://ws.example")


def test_connect_workspace_passes_totp_secret(mocker, monkeypatch):
    monkeypatch.setenv("ALTIUM_TOTP_SECRET", "JBSWY3DPEHPK3PXP")
    api = mocker.Mock()
    ws = mocker.Mock()
    ws.workspace_id = 1
    ws.hosting_url = "https://ws.example"
    ws.name = "Main"
    api.get_user_workspaces.return_value = [ws]
    workspace = mocker.Mock()
    api.login_workspace.return_value = workspace

    session = HarnessSession(api_factory=lambda: api)
    session._api = api
    session._credentials = ("user", "pass")

    assert session.connect_workspace("https://ws.example") is True
    api.login_workspace.assert_called_once_with(
        ws,
        "user",
        "pass",
        oauth_totp_secret="JBSWY3DPEHPK3PXP",
    )
