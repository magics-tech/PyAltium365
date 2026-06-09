from typing import Tuple, Any

import pytest

from py_altium365.altium_api_workspace import AltiumApiWorkspace


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
    item = mocker.Mock()
    api._vault.get_alu_items = mocker.Mock(return_value=[item])

    result = api.get_items_in_folder(folder)

    assert result == [item]
    api._vault.get_alu_items.assert_called_once()


def test_get_items_in_folder_no_guid(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    folder.guid = None

    assert api.get_items_in_folder(folder) == []


def test_get_item_from_guid(mocker):
    api, _ = create_workspace_api(mocker)
    item = mocker.Mock()
    api._vault.get_alu_items = mocker.Mock(return_value=[item])

    result = api.get_item_from_guid("item-guid")

    assert result is item


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
