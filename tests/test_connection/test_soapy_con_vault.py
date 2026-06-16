"""Unit tests for vault SOAP client."""

import pytest

from py_altium365.connection.vault.soapy_con_vault import SoapConVault
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluFolder,
    AluItem,
    AluLifeCycleDefinition,
    AluLifeCycleState,
    AluLifeCycleStateChange,
    AluLifeCycleStateTransition,
    SoapMethodOption,
)


def _make_vault(mocker):
    workspace = mocker.Mock()
    workspace.workspace_url = "https://workspace.example"
    workspace.session_guid = "session-guid"
    return SoapConVault(workspace)


@pytest.mark.anyio
async def test_get_alu_folders(mocker):
    vault = _make_vault(mocker)
    folder = AluFolder(guid="f1", hrid="Folder")
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[folder])))

    folders = await vault.get_alu_folders(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS], p_filter="GUID='f1'")

    assert folders == [folder]
    vault._send_command.assert_called_once()


@pytest.mark.anyio
async def test_get_alu_items(mocker):
    vault = _make_vault(mocker)
    item = AluItem(guid="i1", hrid="Item")
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[item])))

    items = await vault.get_alu_items(p_filter="FolderGUID='f1'")

    assert items == [item]


@pytest.mark.anyio
async def test_get_alu_life_cycle_states(mocker):
    vault = _make_vault(mocker)
    state = AluLifeCycleState(guid="lcs-1")
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[state])))

    result = await vault.get_alu_life_cycle_states()

    assert result == [state]
    vault._send_command.assert_called_once()


@pytest.mark.anyio
async def test_get_alu_life_cycle_states_with_filter(mocker):
    vault = _make_vault(mocker)
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[])))

    await vault.get_alu_life_cycle_states(p_filter="GUID='lcs-1'")

    call_args = vault._send_command.call_args
    assert call_args.kwargs["method"].p_filter == "GUID='lcs-1'"


@pytest.mark.anyio
async def test_get_alu_life_cycle_definitions(mocker):
    vault = _make_vault(mocker)
    definition = AluLifeCycleDefinition(guid="lcd-1")
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[definition])))

    result = await vault.get_alu_life_cycle_definitions()

    assert result == [definition]
    vault._send_command.assert_called_once()


@pytest.mark.anyio
async def test_get_alu_life_cycle_state_changes(mocker):
    vault = _make_vault(mocker)
    change = AluLifeCycleStateChange(guid="lcsc-1", item_revision_guid="rev-1")
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[change])))

    result = await vault.get_alu_life_cycle_state_changes(p_filter="ItemRevisionGUID = 'rev-1'")

    assert result == [change]
    call_args = vault._send_command.call_args
    assert call_args.kwargs["method"].p_filter == "ItemRevisionGUID = 'rev-1'"


@pytest.mark.anyio
async def test_get_alu_life_cycle_state_transitions(mocker):
    vault = _make_vault(mocker)
    transition = AluLifeCycleStateTransition(guid="lcst-1", life_cycle_state_before_guid="state-before")
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[transition])))

    result = await vault.get_alu_life_cycle_state_transitions(p_filter="LifeCycleStateBeforeGUID = 'state-before'")

    assert result == [transition]
    call_args = vault._send_command.call_args
    assert call_args.kwargs["method"].p_filter == "LifeCycleStateBeforeGUID = 'state-before'"


@pytest.mark.anyio
async def test_add_alu_life_cycle_state_changes(mocker):
    vault = _make_vault(mocker)
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock()))

    result = await vault.add_alu_life_cycle_state_changes(
        item_revision_guids=["rev-1"],
        life_cycle_state_transition_guids=["trans-1"],
        life_cycle_state_after_guids=["state-after-1"],
    )

    assert result is True
    vault._send_command.assert_called_once()
    call_args = vault._send_command.call_args
    records = call_args.kwargs["method"].records
    assert len(records) == 1
    assert records[0].item_revision_guid == "rev-1"
    assert records[0].life_cycle_state_transition_guid == "trans-1"
    assert records[0].life_cycle_state_after_guid == "state-after-1"


@pytest.mark.anyio
async def test_add_alu_life_cycle_state_changes_length_mismatch(mocker):
    vault = _make_vault(mocker)
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock())

    result = await vault.add_alu_life_cycle_state_changes(
        item_revision_guids=["rev-1", "rev-2"],
        life_cycle_state_transition_guids=["trans-1"],
        life_cycle_state_after_guids=["state-after-1"],
    )

    assert result is False
    vault._send_command.assert_not_called()
