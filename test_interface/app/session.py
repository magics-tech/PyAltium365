"""Harness session orchestrating PyAltium365 API calls."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from py_altium365.altium_api import AltiumApi
from py_altium365.altium_api_workspace import AltiumApiWorkspace
from py_altium365.base.connection_handler import ConnectionHandler
from py_altium365.connection.components.components_api import ComponentRecord, ComponentsApiClient, ComponentsListPage, ComponentsQuery
from py_altium365.connection.json_con_search_async import JsonConSearchAsync
from py_altium365.connection.soapy_con_service_discovery import ServiceEndpoints
from py_altium365.connection.soapy_con_workspace import UserWorkspaceInfo
from py_altium365.connection.vault.soapy_con_vault_base import AluFolder, AluItem

from test_interface.app.components_patch import ComponentsPatch, PatchError as ComponentsPatchError, apply_patch as apply_components_patch, default_components_query
from test_interface.app.search_patch import PatchError, SearchPatch, apply_patch
from test_interface.app.serializers import ComponentRow, ScenarioDocument, SortFieldRow, component_record_to_row, components_query_to_row
from test_interface.app.trace import TraceEntry, TracingSession


@dataclass
class LoginResult:
    """Portal login outcome."""

    success: bool
    message: str = ""
    workspace_count: int = 0


@dataclass
class SessionStatus:
    """Current harness session state."""

    portal_active: bool = False
    workspace_connected: bool = False
    workspace_name: str = ""
    workspace_url: str = ""
    workspace_count: int = 0
    last_error: str = ""
    has_search: bool = False
    search_count: int = 0


class HarnessSession:
    """Injectable session layer for the test harness."""

    def __init__(self, api_factory: Optional[Callable[[], AltiumApi]] = None, trace_max_entries: int = 100) -> None:
        self._api_factory = api_factory or AltiumApi
        self._api: Optional[AltiumApi] = None
        self._workspace: Optional[AltiumApiWorkspace] = None
        self._search: Optional[JsonConSearchAsync] = None
        self._components_client: Optional[ComponentsApiClient] = None
        self._components_query: ComponentsQuery = default_components_query()
        self._credentials: tuple[str, str] = ("", "")
        self._last_error: str = ""
        self._tracing_session = TracingSession(max_entries=trace_max_entries)
        ConnectionHandler.set_instance(self._tracing_session)

    @property
    def api(self) -> Optional[AltiumApi]:
        return self._api

    @property
    def workspace(self) -> Optional[AltiumApiWorkspace]:
        return self._workspace

    @property
    def search(self) -> Optional[JsonConSearchAsync]:
        return self._search

    def login(self, username: str, password: str) -> LoginResult:
        self.logout()
        self._credentials = (username, password)
        try:
            self._api = self._api_factory()
            result = self._api.login(username, password, return_message=True)
            if result is not True:
                message = result if isinstance(result, str) else "Login failed"
                self._last_error = message
                self._api = None
                return LoginResult(success=False, message=message)
            workspaces = self._api.get_user_workspaces()
            self._last_error = ""
            return LoginResult(success=True, workspace_count=len(workspaces))
        except ConnectionError as exc:
            self._last_error = str(exc)
            self._api = None
            return LoginResult(success=False, message=str(exc))

    def logout(self) -> None:
        self._api = None
        self._workspace = None
        self._search = None
        self._components_client = None
        self._components_query = default_components_query()
        self._credentials = ("", "")
        self._last_error = ""

    def get_workspaces(self) -> List[UserWorkspaceInfo]:
        self._require_portal()
        return self._api.get_user_workspaces()  # type: ignore[union-attr]

    def connect_workspace(self, url_or_id: str) -> bool:
        self._require_portal()
        username, password = self._credentials
        workspace_target: UserWorkspaceInfo | str = url_or_id
        for ws in self._api.get_user_workspaces():  # type: ignore[union-attr]
            if str(ws.workspace_id) == url_or_id or ws.hosting_url == url_or_id or ws.name == url_or_id:
                workspace_target = ws
                break
        try:
            totp_secret = os.environ.get("ALTIUM_TOTP_SECRET")
            workspace = self._api.login_workspace(  # type: ignore[union-attr]
                workspace_target,
                username,
                password,
                oauth_totp_secret=totp_secret,
            )
            if workspace is None:
                self._last_error = "Workspace login failed"
                self._workspace = None
                self._search = None
                return False
            self._workspace = workspace
            self._search = None
            self._components_client = None
            self._components_query = default_components_query()
            self._last_error = ""
            return True
        except ConnectionError as exc:
            self._last_error = str(exc)
            self._workspace = None
            self._search = None
            self._components_client = None
            return False

    def get_service_urls(self) -> ServiceEndpoints:
        self._require_workspace()
        return self._workspace._service_discovery.service_urls  # type: ignore[union-attr]  # pylint: disable=protected-access

    def get_current_workspace_info(self) -> tuple[str, str]:
        self._require_workspace()
        name = self._workspace.workspace_url  # type: ignore[union-attr]
        for ws in self.get_workspaces():
            if ws.hosting_url == self._workspace.workspace_url:  # type: ignore[union-attr]
                name = ws.name
                break
        return name, self._workspace.workspace_url  # type: ignore[union-attr]

    def list_folders(self) -> List[AluFolder]:
        self._require_workspace()
        return self._workspace.get_all_folders()  # type: ignore[union-attr]

    def list_items(self, folder_guid: str) -> List[AluItem]:
        self._require_workspace()
        folder = self._workspace.get_folder_from_guid(folder_guid)  # type: ignore[union-attr]
        if folder is None:
            return []
        return self._workspace.get_items_in_folder(folder)  # type: ignore[union-attr]

    def get_item(self, guid: str) -> Optional[AluItem]:
        self._require_workspace()
        return self._workspace.get_item_from_guid(guid)  # type: ignore[union-attr]

    def create_search(self) -> JsonConSearchAsync:
        self._require_workspace()
        self._search = self._workspace.create_search_object()  # type: ignore[union-attr]
        return self._search

    def apply_patch(self, patch: SearchPatch) -> None:
        self._require_search()
        try:
            apply_patch(self._search, patch)  # type: ignore[arg-type]
            self._last_error = ""
        except PatchError as exc:
            self._last_error = str(exc)
            raise

    def get_search_count(self) -> int:
        self._require_search()
        return self._search.get_current_count()  # type: ignore[union-attr]

    def get_results_page(self, start: int = 0, limit: int = 50) -> list:
        self._require_search()
        from test_interface.app.serializers import search_data_to_row

        results = self._search.get_results_page(start=start, limit=limit)  # type: ignore[union-attr]
        return [search_data_to_row(row) for row in results]

    def get_search_meta(self) -> dict:
        self._require_search()
        facets = []
        for name, faced_type in self._search.get_all_search_names_and_type():  # type: ignore[union-attr]
            support_range = name in self._search.get_all_search_names_range()  # type: ignore[union-attr]
            facets.append({"name": name, "faced_type": faced_type.value, "support_range": support_range})
        return {
            "facets": facets,
            "terms": self._search.get_all_search_parameters(),  # type: ignore[union-attr]
            "ranges": {k: list(v) for k, v in self._search.get_all_search_parameters_range().items()},  # type: ignore[union-attr]
            "wildcard": self._search.get_search_parameter_wildcard(),  # type: ignore[union-attr]
            "sort_fields": [{"name": sf.name, "descending": sf.descending} for sf in self._search.get_sort_fields()],  # type: ignore[union-attr]
            "content_types": self._search.get_search_parameter("ContentType"),  # type: ignore[union-attr]
        }

    def export_scenario(self) -> ScenarioDocument:
        self._require_search()
        ranges = {}
        for name, values in self._search.get_all_search_parameters_range().items():  # type: ignore[union-attr]
            ranges[name] = [values[0], values[1], values[2], values[3]]
        return ScenarioDocument(
            content_types=self._search.get_search_parameter("ContentType"),  # type: ignore[union-attr]
            terms=self._search.get_all_search_parameters(),  # type: ignore[union-attr]
            ranges=ranges,
            wildcard=self._search.get_search_parameter_wildcard(),  # type: ignore[union-attr]
            sort_fields=[SortFieldRow(name=sf.name, descending=sf.descending) for sf in self._search.get_sort_fields()],  # type: ignore[union-attr]
        )

    def import_scenario(self, scenario: ScenarioDocument) -> None:
        if self._search is None:
            self.create_search()
        self.apply_patch(SearchPatch(action="clear_all"))
        if scenario.content_types:
            self.apply_patch(SearchPatch(action="set_content_types", content_types=scenario.content_types, remove_old=True))
        for name, values in scenario.terms.items():
            if name == "ContentType":
                continue
            self.apply_patch(SearchPatch(action="add_term", facet_name=name, values=values))
        for name, values in scenario.ranges.items():
            if len(values) < 4:
                continue
            self.apply_patch(
                SearchPatch(
                    action="set_range",
                    facet_name=name,
                    min_value=float(values[0]),
                    max_value=float(values[1]),
                    min_inclusive=bool(values[2]),
                    max_inclusive=bool(values[3]),
                )
            )
        if scenario.wildcard:
            self.apply_patch(SearchPatch(action="set_wildcard", value=scenario.wildcard))
        if scenario.sort_fields:
            from test_interface.app.search_patch import SortPatch

            self.apply_patch(
                SearchPatch(
                    action="add_sort",
                    sort_fields=[SortPatch(name=sf.name, descending=sf.descending) for sf in scenario.sort_fields],
                )
            )

    def create_components_client(self) -> ComponentsApiClient:
        self._require_workspace()
        self._components_client = self._workspace.create_components_client()  # type: ignore[union-attr]
        return self._components_client

    def get_components_query(self) -> ComponentsQuery:
        self._require_workspace()
        return self._components_query

    def apply_components_patch(self, patch: ComponentsPatch) -> None:
        self._require_workspace()
        try:
            self._components_query = apply_components_patch(self._components_query, patch)
            self._last_error = ""
        except ComponentsPatchError as exc:
            self._last_error = str(exc)
            raise

    def get_components_meta(self) -> dict:
        self._require_workspace()
        from test_interface.app.components_patch import DEFAULT_FIELD_OPTIONS

        return {
            "field_options": DEFAULT_FIELD_OPTIONS,
            "query": components_query_to_row(self._components_query).model_dump(),
        }

    def list_components_page(self, start: int | None = None, limit: int | None = None) -> ComponentsListPage:
        self._require_workspace()
        if self._components_client is None:
            self.create_components_client()
        query = self._components_query
        updates = {}
        if start is not None:
            updates["start"] = start
        if limit is not None:
            updates["limit"] = limit
        if updates:
            query = query.model_copy(update=updates)
        return self._components_client.list_page(query)  # type: ignore[union-attr]

    def list_components_recent(self, updated_after, max_items: int | None = None) -> List[ComponentRow]:
        self._require_workspace()
        if self._components_client is None:
            self.create_components_client()
        records = self._components_client.list_recent(updated_after, max_items=max_items)  # type: ignore[union-attr]
        return [component_record_to_row(record) for record in records]

    def find_component_by_hrid(self, hrid: str) -> Optional[ComponentRecord]:
        self._require_workspace()
        if self._components_client is None:
            self.create_components_client()
        return self._components_client.find_by_hrid(hrid)  # type: ignore[union-attr]

    def get_trace(self) -> List[TraceEntry]:
        return self._tracing_session.get_trace()

    def clear_trace(self) -> None:
        self._tracing_session.clear_trace()

    def status(self) -> SessionStatus:
        workspace_count = 0
        if self._api is not None:
            workspaces = self._api.get_user_workspaces()
            workspace_count = len(workspaces) if workspaces is not None else 0
        workspace_name = ""
        workspace_url = ""
        if self._workspace is not None:
            workspace_name, workspace_url = self.get_current_workspace_info()
        search_count = 0
        if self._search is not None:
            try:
                search_count = self._search.get_current_count()
            except ConnectionError:
                search_count = 0
        return SessionStatus(
            portal_active=self._api is not None,
            workspace_connected=self._workspace is not None,
            workspace_name=workspace_name,
            workspace_url=workspace_url,
            workspace_count=workspace_count,
            last_error=self._last_error,
            has_search=self._search is not None,
            search_count=search_count,
        )

    def _require_portal(self) -> None:
        if self._api is None:
            raise PermissionError("Portal session required")

    def _require_workspace(self) -> None:
        self._require_portal()
        if self._workspace is None:
            raise PermissionError("Workspace session required")

    def _require_search(self) -> None:
        self._require_workspace()
        if self._search is None:
            raise PermissionError("Search session required")
