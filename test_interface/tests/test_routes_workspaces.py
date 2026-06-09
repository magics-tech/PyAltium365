"""Workspace route tests."""

from __future__ import annotations

from py_altium365.connection.soapy_con_service_discovery import ServiceEndpoints


def test_connect_requires_login(client):
    response = client.post("/api/workspaces/connect", json={"url_or_id": "https://ws"})

    assert response.status_code == 401


def test_connect_success(client, mock_api, mocker):
    mock_api.login.return_value = True
    mock_api.get_user_workspaces.return_value = []
    workspace = mocker.Mock()
    workspace.workspace_url = "https://ws"
    workspace._service_discovery.service_urls = ServiceEndpoints(SEARCHBASE="https://search")
    mock_api.login_workspace.return_value = workspace

    client.post("/api/login", json={"username": "u", "password": "p"})

    response = client.post("/api/workspaces/connect", json={"url_or_id": "https://ws"})

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_current_workspace_404(client, mock_api):
    mock_api.login.return_value = True
    mock_api.get_user_workspaces.return_value = []
    client.post("/api/login", json={"username": "u", "password": "p"})

    response = client.get("/api/workspaces/current")

    assert response.status_code == 404
