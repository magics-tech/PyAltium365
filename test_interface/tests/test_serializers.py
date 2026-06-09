"""Serializer unit tests."""

from datetime import datetime

from py_altium365.connection.soapy_con_service_discovery import ServiceEndpoints
from py_altium365.connection.vault.soapy_con_vault_base import AluFolder, AluItem

from test_interface.app.serializers import build_folder_tree, item_to_row, service_endpoints_to_rows, workspace_to_row


def test_workspace_to_row(mocker):
    ws = mocker.Mock()
    ws.workspace_id = 7
    ws.name = "Lab"
    ws.hosting_url = "https://lab"
    ws.display_hosting_url = "lab"
    ws.description = "desc"
    ws.is_default = True

    row = workspace_to_row(ws)

    assert row.workspace_id == 7
    assert row.name == "Lab"


def test_service_url_rows():
    endpoints = ServiceEndpoints(SEARCHBASE="https://search", VAULT="https://vault")

    rows = service_endpoints_to_rows(endpoints)

    kinds = {row.service_kind for row in rows}
    assert "SEARCHBASE" in kinds
    assert "VAULT" in kinds


def test_build_folder_tree():
    root = AluFolder(guid="root", hrid="Root", parent_folder_guid=None)
    child = AluFolder(guid="child", hrid="Child", parent_folder_guid="root")

    tree = build_folder_tree([root, child])

    assert len(tree) == 1
    assert tree[0].guid == "root"
    assert tree[0].children[0].guid == "child"


def test_item_to_row():
    item = AluItem(guid="g1", hrid="R1", description="d", last_modified_at=datetime(2024, 1, 1))

    row = item_to_row(item)

    assert row.guid == "g1"
    assert row.hrid == "R1"
