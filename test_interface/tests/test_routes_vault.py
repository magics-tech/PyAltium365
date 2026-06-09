"""Vault route tests."""

from py_altium365.connection.vault.soapy_con_vault_base import AluFolder, AluItem


def _connect_workspace(client, mock_api, mocker):
    session = client.app.state.session
    workspace = mocker.Mock()
    workspace.get_all_folders.return_value = [AluFolder(guid="f1", hrid="Folder", parent_folder_guid=None)]
    workspace.get_folder_from_guid.return_value = AluFolder(guid="f1", hrid="Folder")
    workspace.get_items_in_folder.return_value = [AluItem(guid="i1", hrid="Item")]
    workspace.get_item_from_guid.return_value = AluItem(guid="i1", hrid="Item")
    session._api = mock_api
    session._workspace = workspace
    session._credentials = ("u", "p")


def test_folders_api(client, mock_api, mocker):
    _connect_workspace(client, mock_api, mocker)
    response = client.get("/api/vault/folders")
    assert response.status_code == 200
    assert response.json()["folders"][0]["guid"] == "f1"


def test_folder_items_api(client, mock_api, mocker):
    _connect_workspace(client, mock_api, mocker)
    response = client.get("/api/vault/folders/f1/items")
    assert response.status_code == 200
    assert response.json()["items"][0]["guid"] == "i1"


def test_item_api(client, mock_api, mocker):
    _connect_workspace(client, mock_api, mocker)
    response = client.get("/api/vault/items/i1")
    assert response.status_code == 200
    assert response.json()["item"]["hrid"] == "Item"


def test_vault_requires_workspace(client):
    assert client.get("/api/vault/folders").status_code == 401
