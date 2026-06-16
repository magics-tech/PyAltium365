"""Sync shim tests — must run in plain def functions (no event loop)."""

import pytest

try:
    import trio  # noqa: F401
    _TRIO_AVAILABLE = True
except ModuleNotFoundError:
    _TRIO_AVAILABLE = False

from py_altium365.sync_compat import SyncAltiumApi, SyncAltiumApiWorkspace

_BACKENDS = ["asyncio"] + (["trio"] if _TRIO_AVAILABLE else [])


def _make_sync_api(mocker, backend: str = "asyncio") -> SyncAltiumApi:
    api = SyncAltiumApi(backend=backend)
    api._async.login = mocker.AsyncMock(return_value=True)
    api._async.get_user_workspaces = mocker.AsyncMock(return_value=[])
    api._async.get_service_url = mocker.AsyncMock(return_value="https://ws.example")
    return api


@pytest.mark.parametrize("backend", _BACKENDS)
def test_sync_login_returns_true(mocker, backend):
    api = _make_sync_api(mocker, backend=backend)

    result = api.login("user@example.com", "password")

    assert result is True
    api._async.login.assert_called_once_with("user@example.com", "password", False)


@pytest.mark.parametrize("backend", _BACKENDS)
def test_sync_get_user_workspaces_returns_list(mocker, backend):
    api = _make_sync_api(mocker, backend=backend)

    result = api.get_user_workspaces()

    assert result == []
    api._async.get_user_workspaces.assert_called_once()


@pytest.mark.parametrize("backend", _BACKENDS)
def test_sync_get_service_url(mocker, backend):
    api = _make_sync_api(mocker, backend=backend)

    result = api.get_service_url("WORKSPACE")

    assert result == "https://ws.example"


def test_sync_login_workspace_returns_none_on_failure(mocker):
    api = SyncAltiumApi()
    api._async.login_workspace = mocker.AsyncMock(return_value=None)

    result = api.login_workspace("https://ws.example", "user", "pass", use_oauth_for_rest=False)

    assert result is None


def test_sync_login_workspace_wraps_async_workspace(mocker):
    from py_altium365.altium_api_workspace import AltiumApiWorkspace

    async_workspace = mocker.Mock(spec=AltiumApiWorkspace)
    api = SyncAltiumApi()
    api._async.login_workspace = mocker.AsyncMock(return_value=async_workspace)

    result = api.login_workspace("https://ws.example", "user", "pass", use_oauth_for_rest=False)

    assert isinstance(result, SyncAltiumApiWorkspace)
    assert result._async is async_workspace
    assert result._backend == "asyncio"


def test_sync_workspace_get_all_folders(mocker):
    from py_altium365.altium_api_workspace import AltiumApiWorkspace
    from py_altium365.connection.vault.soapy_con_vault_base import AluFolder

    async_workspace = mocker.Mock(spec=AltiumApiWorkspace)
    folder = AluFolder(guid="f1", hrid="Folder")
    async_workspace.get_all_folders = mocker.AsyncMock(return_value=[folder])

    shim = SyncAltiumApiWorkspace(async_workspace)
    result = shim.get_all_folders()

    assert result == [folder]
    async_workspace.get_all_folders.assert_called_once()
