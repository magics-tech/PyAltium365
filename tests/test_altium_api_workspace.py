from typing import Tuple, Any

import pytest

from py_altium365.altium_api_workspace import AltiumApiWorkspace
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluItemRevision,
    AluLifeCycleStateTransition,
    AluLifeCycleStateChange,
)


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


@pytest.mark.anyio
async def test_get_all_folders_delegates_to_vault(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    api._vault.get_alu_folders = mocker.AsyncMock(return_value=[folder])

    result = await api.get_all_folders()

    assert result == [folder]
    api._vault.get_alu_folders.assert_called_once()


@pytest.mark.anyio
async def test_get_items_in_folder(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    folder.guid = "folder-guid"
    item = mocker.Mock()
    api._vault.get_alu_items = mocker.AsyncMock(return_value=[item])

    result = await api.get_items_in_folder(folder)

    assert result == [item]
    api._vault.get_alu_items.assert_called_once()


@pytest.mark.anyio
async def test_get_items_in_folder_no_guid(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    folder.guid = None

    assert await api.get_items_in_folder(folder) == []


@pytest.mark.anyio
async def test_get_item_from_guid(mocker):
    api, _ = create_workspace_api(mocker)
    item = mocker.Mock()
    api._vault.get_alu_items = mocker.AsyncMock(return_value=[item])

    result = await api.get_item_from_guid("item-guid")

    assert result is item


@pytest.mark.anyio
async def test_get_item_from_guid_missing(mocker):
    api, _ = create_workspace_api(mocker)
    api._vault.get_alu_items = mocker.AsyncMock(return_value=[])

    assert await api.get_item_from_guid("missing") is None


@pytest.mark.anyio
async def test_get_folder_from_guid(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    api._vault.get_alu_folders = mocker.AsyncMock(return_value=[folder])

    assert await api.get_folder_from_guid("folder-guid") is folder


@pytest.mark.anyio
async def test_get_folders_in_folder(mocker):
    api, _ = create_workspace_api(mocker)
    folder = mocker.Mock()
    folder.guid = "parent-guid"
    child = mocker.Mock()
    api._vault.get_alu_folders = mocker.AsyncMock(return_value=[child])

    assert await api.get_folders_in_folder(folder) == [child]


@pytest.mark.anyio
async def test_get_possible_life_cycle_state_transitions(mocker):
    api, _ = create_workspace_api(mocker)
    revision = AluItemRevision(guid="rev-1", lifecycle_state_guid="state-guid-1")
    transition = AluLifeCycleStateTransition(guid="trans-1", life_cycle_state_before_guid="state-guid-1")
    api._vault.get_alu_life_cycle_state_transitions = mocker.AsyncMock(return_value=[transition])

    result = await api.get_possible_life_cycle_state_transitions(revision)

    assert result == [transition]
    api._vault.get_alu_life_cycle_state_transitions.assert_called_once_with(
        p_filter="LifeCycleStateBeforeGUID = 'state-guid-1'"
    )


@pytest.mark.anyio
async def test_get_possible_life_cycle_state_transitions_no_guid(mocker):
    api, _ = create_workspace_api(mocker)
    revision = AluItemRevision(guid="rev-1", lifecycle_state_guid=None)
    api._vault.get_alu_life_cycle_state_transitions = mocker.AsyncMock()

    result = await api.get_possible_life_cycle_state_transitions(revision)

    assert result == []
    api._vault.get_alu_life_cycle_state_transitions.assert_not_called()


@pytest.mark.anyio
async def test_change_life_cycle_state(mocker):
    api, _ = create_workspace_api(mocker)
    revision = AluItemRevision(guid="rev-1", lifecycle_state_guid="state-before")
    transition = AluLifeCycleStateTransition(guid="trans-1", life_cycle_state_after_guid="state-after-1")
    api._vault.add_alu_life_cycle_state_changes = mocker.AsyncMock(return_value=True)

    result = await api.change_life_cycle_state([revision], [transition])

    assert result is True
    api._vault.add_alu_life_cycle_state_changes.assert_called_once_with(
        item_revision_guids=["rev-1"],
        life_cycle_state_transition_guids=["trans-1"],
        life_cycle_state_after_guids=["state-after-1"],
    )


@pytest.mark.anyio
async def test_change_life_cycle_state_length_mismatch(mocker):
    api, _ = create_workspace_api(mocker)
    revision = AluItemRevision(guid="rev-1")
    api._vault.add_alu_life_cycle_state_changes = mocker.AsyncMock()

    result = await api.change_life_cycle_state([revision], [])

    assert result is False
    api._vault.add_alu_life_cycle_state_changes.assert_not_called()


@pytest.mark.anyio
async def test_get_life_cycle_state_changes_from_item_revision(mocker):
    api, _ = create_workspace_api(mocker)
    revision = AluItemRevision(guid="rev-1")
    change = AluLifeCycleStateChange(guid="change-1", item_revision_guid="rev-1")
    api._vault.get_alu_life_cycle_state_changes = mocker.AsyncMock(return_value=[change])

    result = await api.get_life_cycle_state_changes_from_item_revision(revision)

    assert result == [change]
    api._vault.get_alu_life_cycle_state_changes.assert_called_once_with(
        p_filter="ItemRevisionGUID = 'rev-1'"
    )


@pytest.mark.anyio
async def test_get_life_cycle_state_changes_from_item_revision_no_guid(mocker):
    api, _ = create_workspace_api(mocker)
    revision = AluItemRevision(guid=None)
    api._vault.get_alu_life_cycle_state_changes = mocker.AsyncMock()

    result = await api.get_life_cycle_state_changes_from_item_revision(revision)

    assert result == []
    api._vault.get_alu_life_cycle_state_changes.assert_not_called()
