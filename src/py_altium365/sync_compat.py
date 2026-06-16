"""Synchronous compatibility shim over the async AltiumApi / AltiumApiWorkspace."""

from __future__ import annotations

from typing import List, Optional, Union

import anyio

from py_altium365.altium_api import AltiumApi
from py_altium365.altium_api_workspace import AltiumApiWorkspace
from py_altium365.connection.soapy_con_workspace import UserWorkspaceInfo
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluFolder,
    AluItem,
    AluItemRevision,
    AluLifeCycleDefinition,
    AluLifeCycleState,
    AluLifeCycleStateChange,
    AluLifeCycleStateTransition,
    SoapMethodOption,
)


class SyncAltiumApi:
    """Synchronous wrapper around AltiumApi for callers that cannot use async/await."""

    def __init__(self, backend: str = "asyncio") -> None:
        self._async = AltiumApi()
        self._backend = backend

    def login(self, username: str, password: str, return_message: bool = False) -> Union[str, bool]:
        return anyio.run(self._async.login, username, password, return_message, backend=self._backend)

    def login_workspace(
        self,
        workspace: Union[UserWorkspaceInfo, str],
        username: str,
        password: str,
        return_message: bool = False,
        force_login: bool = False,
        *,
        oauth_refresh_token: Optional[str] = None,
        oauth_client_id: Optional[str] = None,
        oauth_client_secret: Optional[str] = None,
        oauth_totp_code: Optional[str] = None,
        use_oauth_for_rest: bool = True,
    ) -> Optional["SyncAltiumApiWorkspace"]:
        result = anyio.run(
            self._async.login_workspace,
            workspace,
            username,
            password,
            return_message,
            force_login,
            backend=self._backend,
        )
        if result is None:
            return None
        return SyncAltiumApiWorkspace(result, backend=self._backend)

    def get_service_url(self, service, force_request: bool = False) -> Optional[str]:
        return anyio.run(self._async.get_service_url, service, force_request, backend=self._backend)

    def get_user_workspaces(self) -> List[UserWorkspaceInfo]:
        return anyio.run(self._async.get_user_workspaces, backend=self._backend)


class SyncAltiumApiWorkspace:
    """Synchronous wrapper around AltiumApiWorkspace for callers that cannot use async/await."""

    def __init__(self, async_workspace: AltiumApiWorkspace, backend: str = "asyncio") -> None:
        self._async = async_workspace
        self._backend = backend

    def get_all_folders(self) -> List[AluFolder]:
        return anyio.run(self._async.get_all_folders, backend=self._backend)

    def get_items_in_folder(self, folder: AluFolder) -> List[AluItem]:
        return anyio.run(self._async.get_items_in_folder, folder, backend=self._backend)

    def get_item_from_guid(self, guid: str) -> Optional[AluItem]:
        return anyio.run(self._async.get_item_from_guid, guid, backend=self._backend)

    def get_folder_from_guid(self, guid: str) -> Optional[AluFolder]:
        return anyio.run(self._async.get_folder_from_guid, guid, backend=self._backend)

    def get_folders_in_folder(self, folder: AluFolder, options: Optional[List[SoapMethodOption]] = None) -> List[AluFolder]:
        return anyio.run(self._async.get_folders_in_folder, folder, options, backend=self._backend)

    def get_possible_life_cycle_state_transitions(self, item_revision: AluItemRevision) -> List[AluLifeCycleStateTransition]:
        return anyio.run(self._async.get_possible_life_cycle_state_transitions, item_revision, backend=self._backend)

    def change_life_cycle_state(
        self,
        item_revisions: List[AluItemRevision],
        life_cycle_state_transitions: List[AluLifeCycleStateTransition],
    ) -> bool:
        return anyio.run(
            self._async.change_life_cycle_state,
            item_revisions,
            life_cycle_state_transitions,
            backend=self._backend,
        )

    def get_life_cycle_state_changes_from_item_revision(self, item_revision: AluItemRevision) -> List[AluLifeCycleStateChange]:
        return anyio.run(self._async.get_life_cycle_state_changes_from_item_revision, item_revision, backend=self._backend)

    def get_life_cycle_states(self) -> List[AluLifeCycleState]:
        return anyio.run(self._async.get_life_cycle_states, backend=self._backend)

    def get_life_cycle_definitions(self) -> List[AluLifeCycleDefinition]:
        return anyio.run(self._async.get_life_cycle_definitions, backend=self._backend)
