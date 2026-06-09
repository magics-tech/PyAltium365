"""Search route tests."""


def _connected_with_search(client, mock_api, mocker):
    mock_api.get_user_workspaces.return_value = []
    session = client.app.state.session
    search = mocker.Mock()
    search.get_all_search_names_and_type.return_value = []
    search.get_all_search_names_range.return_value = []
    search.get_sort_fields.return_value = []
    search.get_search_parameter_wildcard.return_value = None
    search.get_all_search_parameters.return_value = {}
    search.get_all_search_parameters_range.return_value = {}
    search.get_search_parameter.return_value = []
    search.get_current_count.return_value = 5
    search.get_results_page.return_value = []

    workspace = mocker.Mock()
    workspace.workspace_url = "https://ws.example"
    workspace.create_search_object.return_value = search
    session._api = mock_api
    session._workspace = workspace
    session._search = search
    session._credentials = ("u", "p")


def test_create_search(client, mock_api, mocker):
    mock_api.get_user_workspaces.return_value = []
    session = client.app.state.session
    search = mocker.Mock()
    search.get_all_search_names_and_type.return_value = []
    search.get_all_search_names_range.return_value = []
    search.get_sort_fields.return_value = []
    search.get_search_parameter_wildcard.return_value = None
    search.get_all_search_parameters.return_value = {}
    search.get_all_search_parameters_range.return_value = {}
    search.get_search_parameter.return_value = []
    search.get_current_count.return_value = 0
    workspace = mocker.Mock()
    workspace.workspace_url = "https://ws.example"
    workspace.create_search_object.return_value = search
    session._api = mock_api
    session._workspace = workspace
    session._credentials = ("u", "p")

    response = client.post("/api/search")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_patch_search(client, mock_api, mocker):
    _connected_with_search(client, mock_api, mocker)
    response = client.patch(
        "/api/search",
        json={"action": "set_content_types", "content_types": ["Component"], "remove_old": True},
    )
    assert response.status_code == 200


def test_search_count(client, mock_api, mocker):
    _connected_with_search(client, mock_api, mocker)
    response = client.get("/api/search/count")
    assert response.status_code == 200
    assert response.json()["count"] == 5
