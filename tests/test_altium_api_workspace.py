from typing import Tuple, Any

import pytest

from py_altium365.altium_api_workspace import AltiumApiWorkspace
from py_altium365.connection.vault.soapy_con_vault_base import AluItem


def create_workspace_api(mocker) -> Tuple[AltiumApiWorkspace, Any]:
    workspace_url = "test_workspace_url"
    service_discovery = mocker.Mock()
    service_discovery.user_info.session_id = "test_session_id"
    service_discovery.service_urls.SEARCHBASE = "test_search_base_url"
    return AltiumApiWorkspace(workspace_url, service_discovery), service_discovery


def test_init(mocker):
    workspace_url = "test_workspace_url"
    service_discovery = mocker.Mock()
    service_discovery.user_info.session_id = "test_session_id"
    service_discovery.service_urls.SEARCHBASE = "test_search_base_url"

    api_workspace = AltiumApiWorkspace(workspace_url, service_discovery)
    assert api_workspace.workspace_url == workspace_url
    assert api_workspace._service_discovery == service_discovery
    assert api_workspace.session_guid == service_discovery.user_info.session_id
    assert api_workspace._service_discovery.service_urls.SEARCHBASE == "test_search_base_url"


def test_init_no_user_info(mocker):
    workspace_url = "test_workspace_url"
    service_discovery = mocker.Mock()
    service_discovery.user_info = None

    with pytest.raises(ConnectionError):
        AltiumApiWorkspace(workspace_url, service_discovery)


def test_init_no_search_base_url(mocker):
    workspace_url = "test_workspace_url"
    service_discovery = mocker.Mock()
    service_discovery.user_info.session_id = "test_session_id"
    service_discovery.service_urls.SEARCHBASE = None

    with pytest.raises(ConnectionError):
        AltiumApiWorkspace(workspace_url, service_discovery)


def test_create_search_object(mocker):
    api, service_discovery = create_workspace_api(mocker)
    service_discovery.service_urls.SEARCHBASE = "test_search_base_url"
    mocker.patch("py_altium365.altium_api_workspace.JsonConSearchAsync", return_value="TEST")

    assert api.create_search_object() == "TEST"


def test_create_components_client(mocker):
    api, service_discovery = create_workspace_api(mocker)
    service_discovery.service_urls.Library_Components_Api = "https://ws/components/api/components"
    mocker.patch("py_altium365.altium_api_workspace.ConnectionHandler.get_instance", return_value=mocker.Mock())
    mocker.patch("py_altium365.altium_api_workspace.ComponentsApiClient", return_value="COMPONENTS")

    assert api.create_components_client() == "COMPONENTS"


def test_create_search_object_no_search_base_url(mocker):
    api, service_discovery = create_workspace_api(mocker)
    service_discovery.service_urls.SEARCHBASE = None

    with pytest.raises(ConnectionError):
        api.create_search_object()


def test_get_all_folders_delegates_to_vault(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    api._vault.get_alu_folders = mocker.Mock(return_value=[folder])

    result = api.get_all_folders()

    assert result == [folder]
    api._vault.get_alu_folders.assert_called_once()


def test_get_items_in_folder(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    folder.guid = "folder-guid"
    item = AluItem(guid="item-guid")
    api._vault.get_alu_items = mocker.Mock(return_value=[item])

    result = api.get_items_in_folder(folder)

    assert result == [item]
    assert result[0]._altium_workspace is api
    api._vault.get_alu_items.assert_called_once()


def test_get_items_in_folder_no_guid(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    folder.guid = None

    assert api.get_items_in_folder(folder) == []


def test_get_item_from_guid(mocker):
    api, _ = create_workspace_api(mocker)
    item = AluItem(guid="item-guid")
    api._vault.get_alu_items = mocker.Mock(return_value=[item])

    result = api.get_item_from_guid("item-guid")

    assert result is item
    assert result._altium_workspace is api


def test_get_item_from_guid_missing(mocker):
    api, _ = create_workspace_api(mocker)
    api._vault.get_alu_items = mocker.Mock(return_value=[])

    assert api.get_item_from_guid("missing") is None


def test_get_folder_from_guid(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    api._vault.get_alu_folders = mocker.Mock(return_value=[folder])

    assert api.get_folder_from_guid("folder-guid") is folder


def test_get_folders_in_folder(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    folder.guid = "parent-guid"
    child = mocker.Mock()
    api._vault.get_alu_folders = mocker.Mock(return_value=[child])

    assert api.get_folders_in_folder(folder) == [child]
