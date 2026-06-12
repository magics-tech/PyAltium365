"""Unit tests for vault SOAP client."""

from py_altium365.connection.vault.soapy_con_vault import SoapConVault
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluFolder,
    AluItem,
    AluItemRevision,
    AluItemRevisionLink,
    SoapMethodOption,
)


def test_get_alu_folders(mocker):
    workspace = mocker.Mock()
    workspace.workspace_url = "https://workspace.example"
    workspace.session_guid = "session-guid"
    vault = SoapConVault(workspace)
    folder = AluFolder(guid="f1", hrid="Folder")
    mocker.patch.object(vault, "_send_command", return_value=mocker.Mock(records=[folder]))

    folders = vault.get_alu_folders(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS], p_filter="GUID='f1'")

    assert folders == [folder]
    vault._send_command.assert_called_once()


def test_get_alu_items(mocker):
    workspace = mocker.Mock()
    workspace.workspace_url = "https://workspace.example"
    workspace.session_guid = "session-guid"
    vault = SoapConVault(workspace)
    item = AluItem(guid="i1", hrid="Item")
    mocker.patch.object(vault, "_send_command", return_value=mocker.Mock(records=[item]))

    items = vault.get_alu_items(p_filter="FolderGUID='f1'")

    assert items == [item]
    vault._send_command.assert_called_once()


def test_get_alu_item_revisions(mocker):
    workspace = mocker.Mock()
    workspace.workspace_url = "https://workspace.example"
    workspace.session_guid = "session-guid"
    vault = SoapConVault(workspace)
    revision = AluItemRevision(guid="rev-1")
    mocker.patch.object(vault, "_send_command", return_value=mocker.Mock(records=[revision]))

    revisions = vault.get_alu_item_revisions(p_filter="ItemGUID='item-1'")

    assert revisions == [revision]


def test_get_alu_item_revision_links(mocker):
    workspace = mocker.Mock()
    workspace.workspace_url = "https://workspace.example"
    workspace.session_guid = "session-guid"
    vault = SoapConVault(workspace)
    link = AluItemRevisionLink(parent_item_revision_guid="parent-rev", child_item_revision_guid="child-rev")
    mocker.patch.object(vault, "_send_command", return_value=mocker.Mock(records=[link]))

    links = vault.get_alu_item_revision_links(p_filter="ParentItemRevisionGUID='parent-rev'")

    assert links == [link]
