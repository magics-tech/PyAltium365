"""Unit tests for Altium browser OAuth helpers."""

from unittest.mock import MagicMock

from py_altium365.connection.oauth.altium_identity_oauth import parse_workspace_home_tokens
from py_altium365.connection.rest_con import RestCon


def test_parse_workspace_home_tokens_extracts_gsid_and_session_id():
    html = """
    <script>
    window.__gsid = 'gsid-token';
    window.__sessionId = 'session-token';
    </script>
    """
    gsid, session_id = parse_workspace_home_tokens(html)
    assert gsid == "gsid-token"
    assert session_id == "session-token"


def test_rest_con_uses_x_alugsid_header():
    client = RestCon(
        session=MagicMock(),
        url="https://ws.example/components/api/components",
        access_token="jwt-token",
        auth_mode="alugsid",
    )
    headers = client._auth_headers()
    assert headers["x-alugsid"] == "jwt-token"
    assert "Authorization" not in headers
