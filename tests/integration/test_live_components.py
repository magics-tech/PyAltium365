"""Live Components REST API smoke test."""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_live_components_list_page(altium_credentials):
    user, password = altium_credentials
    from py_altium365.altium_api import AltiumApi

    api = AltiumApi()
    assert api.login(user, password) is True
    workspaces = api.get_user_workspaces()
    if not workspaces:
        pytest.skip("No workspaces available for this account")

    workspace = api.login_workspace(workspaces[0], user, password)
    assert workspace is not None

    client = workspace.create_components_client()
    page = client.list_page(limit=10)
    assert page.total >= 0
    if page.items:
        first = page.items[0]
        assert first.hrid
        assert first.update_date is not None
