import pytest

from py_altium365.altium_api import AltiumApi
from py_altium365.base.enums import PrtGlobalService


@pytest.mark.anyio
async def test_user_login_correct(mocker):
    api = AltiumApi()

    mock_portal_con = mocker.AsyncMock()
    mock_portal_con.login_user.return_value.success = True
    mock_portal_con.login_user.return_value.session_handle = "test_session_handle"
    api._portal_con = mock_portal_con

    mock_soapy_con_workspace = mocker.patch("py_altium365.altium_api.SoapyConWorkspace")
    mock_soapy_con_workspace.return_value = "test_soapy_con_workspace"

    assert await api.login("test_user", "test_pass")
    assert api._session_guid == "test_session_handle"
    assert api._workspace_con == "test_soapy_con_workspace"
    assert mock_portal_con.login_user.called
    assert mock_soapy_con_workspace.called


@pytest.mark.anyio
async def test_user_login_incorrect(mocker):
    api = AltiumApi()

    mock_portal_con = mocker.AsyncMock()
    mock_portal_con.login_user.return_value.success = False
    mock_portal_con.login_user.return_value.message = "test_message"
    api._portal_con = mock_portal_con

    assert not await api.login("test_user", "test_pass")
    assert api._session_guid is None
    assert api._workspace_con is None
    assert mock_portal_con.login_user.called


@pytest.mark.anyio
async def test_user_login_incorrect_with_message(mocker):
    api = AltiumApi()

    mock_portal_con = mocker.AsyncMock()
    mock_portal_con.login_user.return_value.success = False
    mock_portal_con.login_user.return_value.message = "test_message"
    api._portal_con = mock_portal_con

    assert await api.login("test_user", "test_pass", return_message=True) == "test_message"
    assert api._session_guid is None
    assert api._workspace_con is None
    assert mock_portal_con.login_user.called


@pytest.mark.anyio
async def test_user_login_connection_error(mocker):
    api = AltiumApi()

    mock_portal_con = mocker.AsyncMock()
    mock_portal_con.login_user.side_effect = ConnectionError
    api._portal_con = mock_portal_con

    assert not await api.login("test_user", "test_pass")
    assert api._session_guid is None
    assert api._workspace_con is None
    assert mock_portal_con.login_user.called


@pytest.mark.anyio
async def test_login_workspace(mocker):
    api = AltiumApi()

    api.login = mocker.AsyncMock(return_value=True)

    mock_sd_class = mocker.patch("py_altium365.altium_api.SoapyConServiceDiscovery")
    mock_sd_instance = mocker.AsyncMock()
    mock_sd_instance.user_info = True
    mock_sd_class.return_value = mock_sd_instance

    mocker.patch("py_altium365.altium_api.AltiumIdentityOAuth")
    mocker.patch("py_altium365.altium_api.AltiumApiWorkspace", return_value="test_workspace")

    assert await api.login_workspace("test_workspace", "test_user", "test_pass", use_oauth_for_rest=False) == "test_workspace"


@pytest.mark.anyio
async def test_get_service_url_cache(mocker):
    api = AltiumApi()

    api._service_urls = {
        PrtGlobalService.WORKSPACE.name: "test_workspace_url",
    }

    mock_portal_con = mocker.AsyncMock()
    mock_portal_con.get_prt_global_service_url.return_value = "test_portal_url"
    api._portal_con = mock_portal_con

    assert await api.get_service_url(PrtGlobalService.WORKSPACE) == "test_workspace_url"
    assert await api.get_service_url(PrtGlobalService.WORKSPACE, True) == "test_portal_url"
    mock_portal_con.get_prt_global_service_url.assert_called_once_with(PrtGlobalService.WORKSPACE, None)


@pytest.mark.anyio
async def test_get_service_url_no_cache(mocker):
    api = AltiumApi()

    api._service_urls = {}

    mock_portal_con = mocker.AsyncMock()
    mock_portal_con.get_prt_global_service_url.return_value = "test_portal_url"
    api._portal_con = mock_portal_con

    assert await api.get_service_url(PrtGlobalService.WORKSPACE) == "test_portal_url"
    mock_portal_con.get_prt_global_service_url.assert_called_once_with(PrtGlobalService.WORKSPACE, None)
