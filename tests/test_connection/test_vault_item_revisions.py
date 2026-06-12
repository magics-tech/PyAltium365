"""Unit tests for vault item revision helpers."""

from datetime import datetime
from pathlib import Path

from py_altium365.altium_api_workspace import AltiumApiWorkspace
from py_altium365.connection.soapy_con import SoapBody, SoapEnvelope, SoapHeader
from py_altium365.connection.vault.soapy_con_vault import SoapResponseVaultGetAluItemRevisions
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluItem,
    AluItemRevision,
    AluItemRevisionLink,
    pick_latest_item_revision,
)

_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def create_workspace_api(mocker):
    service_discovery = mocker.Mock()
    service_discovery.user_info.session_id = "test_session_id"
    service_discovery.service_urls.SEARCHBASE = "test_search_base_url"
    return AltiumApiWorkspace("https://workspace.example", service_discovery)


def test_item_revision_xml_parses_revision_id():
    xml = (_FIXTURES_DIR / "item_revisions_response.xml").read_bytes()
    shape = SoapEnvelope[SoapHeader, SoapBody[SoapResponseVaultGetAluItemRevisions]]
    revision = shape.from_xml(xml).body.method.records[0]

    assert revision.revision_id == "1"
    assert revision.item_guid == "AE505432-BEDD-463D-B5DA-A85E1C0D88F1"
    assert revision.comment == "61202421721"


def test_pick_latest_item_revision_prefers_highest_revision_id():
    older = AluItemRevision(guid="rev-1", revision_id="1")
    newer = AluItemRevision(guid="rev-2", revision_id="2")

    assert pick_latest_item_revision([older, newer]) is newer


def test_alu_item_get_name():
    item = AluItem(hrid="CMP-0001")
    assert item.get_name() == "CMP-0001"


def test_alu_item_get_latest_item_revision_from_embedded_revisions(mocker):
    api = create_workspace_api(mocker)
    revision = AluItemRevision(guid="rev-1", is_active=True, release_date=datetime(2025, 1, 1))
    item = AluItem(guid="item-1", hrid="CMP-0001", revisions=[revision])
    api._bind_vault_item(item)

    latest = item.get_latest_item_revision()

    assert latest is revision
    assert latest._altium_workspace is api


def test_alu_item_get_latest_item_revision_fetches_from_workspace(mocker):
    api = create_workspace_api(mocker)
    revision = AluItemRevision(guid="rev-1", is_active=True, release_date=datetime(2025, 1, 1))
    item = AluItem(guid="item-1", hrid="CMP-0001")
    api._bind_vault_item(item)
    api.get_item_revisions_for_item = mocker.Mock(return_value=[revision])

    latest = item.get_latest_item_revision()

    assert latest is revision
    api.get_item_revisions_for_item.assert_called_once_with(item)


def test_get_child_item_revisions_uses_embedded_child_revision(mocker):
    api = create_workspace_api(mocker)
    child = AluItemRevision(guid="child-rev", item_guid="child-item", item_hrid="SYM-0001")
    link = AluItemRevisionLink(parent_item_revision_guid="parent-rev", child_item_revision=child)
    parent = AluItemRevision(guid="parent-rev", item_guid="parent-item")
    api._bind_vault_revision(parent)
    api._vault.get_alu_item_revision_links = mocker.Mock(return_value=[link])

    children = api.get_child_item_revisions("parent-rev")

    assert children == [child]
    assert child._altium_workspace is api


def test_get_child_item_revisions_resolves_child_guid(mocker):
    api = create_workspace_api(mocker)
    child = AluItemRevision(guid="child-rev", item_guid="child-item", item_hrid="FP-0001")
    link = AluItemRevisionLink(parent_item_revision_guid="parent-rev", child_item_revision_guid="child-rev")
    api._vault.get_alu_item_revision_links = mocker.Mock(return_value=[link])
    api.get_item_revision_from_guid = mocker.Mock(return_value=child)

    children = api.get_child_item_revisions("parent-rev")

    assert children == [child]
    api.get_item_revision_from_guid.assert_called_once_with("child-rev")


def test_alu_item_revision_get_item_and_children(mocker):
    api = create_workspace_api(mocker)
    item = AluItem(guid="child-item", hrid="SYM-0001")
    child = AluItemRevision(guid="child-rev", item_guid="child-item")
    parent = AluItemRevision(guid="parent-rev", item_guid="child-item")
    api._bind_vault_revision(parent)
    api._bind_vault_revision(child)
    api.get_item_from_guid = mocker.Mock(return_value=item)
    api.get_child_item_revisions = mocker.Mock(return_value=[child])

    assert parent.get_item() is item
    assert parent.get_child_item_revisions() == [child]
