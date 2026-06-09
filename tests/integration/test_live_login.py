"""Live portal login smoke test."""

from __future__ import annotations

import pytest

from py_altium365.altium_api import AltiumApi


@pytest.mark.integration
def test_live_portal_login(altium_credentials):
    user, password = altium_credentials
    api = AltiumApi()
    assert api.login(user, password) is True
    workspaces = api.get_user_workspaces()
    assert isinstance(workspaces, list)
