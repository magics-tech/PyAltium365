"""Unit tests for vault SOAP client."""

from pathlib import Path

from py_altium365.connection.soapy_con import SoapBody, SoapEnvelope, SoapHeader
from py_altium365.connection.vault.soapy_con_vault import SoapConVault, SoapResponseVaultGetAluItemRevisionLinks
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


def test_item_revision_link_xml_parses_child_guid_before_nested_revision():
    xml = (Path(__file__).parent.parent / "fixtures" / "item_revision_links_response.xml").read_bytes()
    shape = SoapEnvelope[SoapHeader, SoapBody[SoapResponseVaultGetAluItemRevisionLinks]]
    link = shape.from_xml(xml).body.method.records[0]

    assert link.parent_item_revision_guid == "PARENT-GUID"
    assert link.child_item_revision_guid == "35C7CB7F-D7AA-4207-B748-F68BE91242A7"
    assert link.child_item_revision is not None
    assert link.child_item_revision.guid == "35C7CB7F-D7AA-4207-B748-F68BE91242A7"


def test_get_alu_item_revision_links(mocker):
    workspace = mocker.Mock()
    workspace.workspace_url = "https://workspace.example"
    workspace.session_guid = "session-guid"
    vault = SoapConVault(workspace)
    link = AluItemRevisionLink(parent_item_revision_guid="parent-rev", child_item_revision_guid="child-rev")
    mocker.patch.object(vault, "_send_command", return_value=mocker.Mock(records=[link]))

    links = vault.get_alu_item_revision_links(p_filter="ParentItemRevisionGUID='parent-rev'")

    assert links == [link]
