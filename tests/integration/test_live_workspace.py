"""Live workspace connection smoke test."""

from __future__ import annotations

import pytest

from py_altium365.altium_api import AltiumApi


@pytest.mark.integration
def test_live_workspace_connect(altium_credentials):
    user, password = altium_credentials
    api = AltiumApi()
    assert api.login(user, password) is True
    workspaces = api.get_user_workspaces()
    if not workspaces:
        pytest.skip("No workspaces available for this account")

    workspace = api.login_workspace(workspaces[0], user, password)
    assert workspace is not None
    assert workspace.session_guid
    assert workspace._service_discovery.service_urls.SEARCHBASE  # noqa: SLF001
