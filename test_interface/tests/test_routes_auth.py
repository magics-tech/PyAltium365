"""Auth route tests."""

from __future__ import annotations


def test_api_login_success(client, mock_api):
    mock_api.login.return_value = True
    mock_api.get_user_workspaces.return_value = []

    response = client.post("/api/login", json={"username": "u", "password": "p"})

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["status"]["portal_active"] is True


def test_api_logout(client, mock_api):
    mock_api.login.return_value = True
    mock_api.get_user_workspaces.return_value = []
    client.post("/api/login", json={"username": "u", "password": "p"})

    response = client.post("/api/logout")

    assert response.status_code == 200
    assert response.json()["status"]["portal_active"] is False


def test_api_status(client):
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json()["status"]["portal_active"] is False


def test_login_form_renders(client, mock_api):
    mock_api.login.return_value = True
    mock_api.get_user_workspaces.return_value = []

    response = client.post("/login", data={"username": "u", "password": "p"})

    assert response.status_code == 200
    assert "portal" in response.text.lower()
