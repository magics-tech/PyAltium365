"""Unit tests for vault SOAP client."""

import pytest

from py_altium365.connection.soapy_con import SoapBody, SoapEnvelopeNoHeader
from py_altium365.connection.vault.soapy_con_vault import (
    AluDownloadUrl,
    SoapConVault,
    SoapResponseVaultGetItemRevisionDownloadURLs,
)
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluFolder,
    AluItem,
    AluItemRevision,
    AluItemRevisionLink,
    AluLifeCycleDefinition,
    AluLifeCycleState,
    AluLifeCycleStateChange,
    AluLifeCycleStateTransition,
    SoapMethodOption,
)

# Real GetALU_ItemRevisionDownloadURLs response captured from the Altium 365
# workspace vault SOAP endpoint, with identifiers scrubbed. Locks the wire
# contract the parser must satisfy.
_DOWNLOAD_URLS_RESPONSE_XML = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/">'
    "<soap-env:Body>"
    '<GetALU_ItemRevisionDownloadURLsResponse xmlns="http://tempuri.org/">'
    '<MethodResult xmlns:i="http://www.w3.org/2001/XMLSchema-instance">'
    "<Success>true</Success><Results><item>"
    "<Message/><Success>true</Success>"
    "<URL>https://ws.example/vault/DownloadRevision?SessionID=S&amp;RevisionGUID=rev-1</URL>"
    "<Size>0</Size>"
    "</item></Results></MethodResult>"
    "</GetALU_ItemRevisionDownloadURLsResponse>"
    "</soap-env:Body></soap-env:Envelope>"
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
async def test_get_alu_item_revisions(mocker):
    vault = _make_vault(mocker)
    revision = AluItemRevision(guid="rev-1", item_hrid="SYM-1")
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[revision])))

    result = await vault.get_alu_item_revisions(p_filter="ItemGUID = 'item-1'")

    assert result == [revision]
    call_args = vault._send_command.call_args
    assert call_args.kwargs["method"].p_filter == "ItemGUID = 'item-1'"
    assert call_args.kwargs["method"].session_handle == "session-guid"


@pytest.mark.anyio
async def test_get_alu_item_revision_links(mocker):
    vault = _make_vault(mocker)
    link = AluItemRevisionLink(
        guid="link-1",
        parent_item_revision_guid="parent-rev",
        child_item_revision_guid="child-rev",
    )
    mocker.patch.object(vault, "_send_command", new=mocker.AsyncMock(return_value=mocker.Mock(records=[link])))

    result = await vault.get_alu_item_revision_links(p_filter="ParentItemRevisionGUID='parent-rev'")

    assert result == [link]
    call_args = vault._send_command.call_args
    assert call_args.kwargs["method"].p_filter == "ParentItemRevisionGUID='parent-rev'"


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


def test_download_urls_response_parses_real_xml():
    """The response model must parse the real on-the-wire SOAP XML."""
    shape = SoapEnvelopeNoHeader[SoapBody[SoapResponseVaultGetItemRevisionDownloadURLs]]
    parsed = shape.from_xml(_DOWNLOAD_URLS_RESPONSE_XML.encode("utf-8")).body.method

    assert parsed.method_result is not None
    assert parsed.method_result.success is True
    assert len(parsed.method_result.results) == 1
    result = parsed.method_result.results[0]
    assert result.success is True
    assert result.url == "https://ws.example/vault/DownloadRevision?SessionID=S&RevisionGUID=rev-1"


@pytest.mark.anyio
async def test_get_item_revision_download_urls(mocker):
    vault = _make_vault(mocker)
    download = AluDownloadUrl(success=True, url="https://ws.example/vault/DownloadRevision?RevisionGUID=rev-1")
    method_result = mocker.Mock(results=[download])
    mocker.patch.object(
        vault, "_send_command",
        new=mocker.AsyncMock(return_value=mocker.Mock(method_result=method_result)),
    )

    results = await vault.get_item_revision_download_urls(["rev-1"])

    assert results == [download]
    call_args = vault._send_command.call_args
    assert call_args.kwargs["method"].item_revision_guid_list == ["rev-1"]
    assert call_args.kwargs["method"].session_handle == "session-guid"


@pytest.mark.anyio
async def test_get_item_revision_download_urls_empty_result(mocker):
    vault = _make_vault(mocker)
    mocker.patch.object(
        vault, "_send_command",
        new=mocker.AsyncMock(return_value=mocker.Mock(method_result=None)),
    )

    results = await vault.get_item_revision_download_urls(["rev-1"])

    assert results == []


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
