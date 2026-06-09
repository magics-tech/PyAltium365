"""Live searchasync smoke test."""

from __future__ import annotations

import pytest

from py_altium365.altium_api import AltiumApi
from py_altium365.connection.json_con_search_async import SearchDataType


@pytest.mark.integration
def test_live_search_count(altium_credentials):
    user, password = altium_credentials
    api = AltiumApi()
    assert api.login(user, password) is True
    workspaces = api.get_user_workspaces()
    if not workspaces:
        pytest.skip("No workspaces available for this account")

    workspace = api.login_workspace(workspaces[0], user, password)
    assert workspace is not None

    search = workspace.create_search_object()
    search.add_content_search_parameter(SearchDataType.COMPONENT)
    count = search.get_current_count()
    assert isinstance(count, int)
    assert count >= 0
