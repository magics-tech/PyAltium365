"""Live workspace OAuth login smoke test (requires TOTP secret when MFA is enabled)."""

from __future__ import annotations

import pytest

from py_altium365.altium_api import AltiumApi


@pytest.mark.integration
def test_live_workspace_login(altium_credentials, altium_totp_secret):
    user, password = altium_credentials
    if not altium_totp_secret:
        pytest.skip("ALTIUM_TOTP_SECRET must be set for workspace OAuth login with MFA")

    api = AltiumApi()
    assert api.login(user, password) is True
    workspaces = api.get_user_workspaces()
    assert workspaces

    workspace = api.login_workspace(
        workspaces[0],
        user,
        password,
        oauth_totp_secret=altium_totp_secret,
    )
    assert workspace is not None
