from typing import Optional
from urllib.parse import urlparse

from py_altium365.base.connection_handler import ConnectionHandler
from py_altium365.connection.components.components_api import ComponentsApiClient
from py_altium365.connection.json_con_search_async import JsonConSearchAsync
from py_altium365.connection.soapy_con_service_discovery import SoapyConServiceDiscovery
from py_altium365.connection.vault.soapy_con_vault import SoapConVault
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluFolder,
    AluItem,
    AluLifeCycleDefinition,
    AluLifeCycleState,
    AluLifeCycleStateChange,
    AluLifeCycleStateTransition,
    AluItemRevision,
    SoapMethodOption,
)

_DEFAULT_COMPONENTS_API_PATH = "/components/api/components"


class AltiumApiWorkspace:
    """Altium API workspace class"""

    def __init__(
        self,
        workspace_url: str,
        service_discovery: SoapyConServiceDiscovery,
        *,
        oauth_access_token: Optional[str] = None,
        oauth_uses_cookies: bool = False,
    ):
        """
        Initialize the Altium API workspace object
        :param workspace_url: The URL of the workspace
        :param service_discovery: The service discovery object
        """

        if service_discovery.user_info is None:
            raise ConnectionError("Failed to get user info")
        self.workspace_url: str = workspace_url
        self._service_discovery: SoapyConServiceDiscovery = service_discovery
        self.session_guid: str = service_discovery.user_info.session_id
        self._oauth_access_token = oauth_access_token
        self._oauth_uses_cookies = oauth_uses_cookies
        if self._service_discovery.service_urls.SEARCHBASE is None:
            raise ConnectionError("Failed to get search base URL")
        self._vault = SoapConVault(self)

    def create_search_object(self) -> JsonConSearchAsync:
        """
        Create a search object
        :return:
        """
        if self._service_discovery.service_urls.SEARCHBASE is None:
            raise ConnectionError("Failed to get search base URL")
        return JsonConSearchAsync(self, self._service_discovery.service_urls.SEARCHBASE, self.session_guid, self._workspace_host())

    def create_components_client(self) -> ComponentsApiClient:
        """Create a Components REST API client for this workspace."""
        base_url = self._components_api_url()
        if self._oauth_access_token:
            auth_mode = "alugsid"
        elif self._oauth_uses_cookies:
            auth_mode = "cookies"
        else:
            auth_mode = "afs"
        return ComponentsApiClient(
            ConnectionHandler.get_instance(),
            base_url,
            self.session_guid,
            access_token=self._oauth_access_token,
            auth_mode=auth_mode,
        )

    def _normalized_workspace_base(self) -> str:
        workspace_base = self.workspace_url.rstrip("/")
        if workspace_base.endswith(":443"):
            workspace_base = workspace_base[:-4]
        return workspace_base

    def _workspace_host(self) -> str:
        return urlparse(self._normalized_workspace_base()).netloc

    def _components_api_url(self) -> str:
        """Build the workspace Components REST URL used by the Altium 365 web UI.

        Service discovery's ``Library.Components.Api`` points at a regional gateway
        (for example ``eur.365.altium.com/librarycomponentsapi/api``) that does not
        serve the same list contract as the workspace endpoint below.
        """
        return f"{self._normalized_workspace_base()}{_DEFAULT_COMPONENTS_API_PATH}"

    def get_item_from_guid(self, guid: str) -> Optional[AluItem]:
        """
        Get an item from the vault using its GUID
        :param guid: The GUID of the item to retrieve
        :return: A list of AluItem objects matching the GUID
        """
        items = self._vault.get_alu_items(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS], p_filter="GUID='" + guid + "'")
        return items[0] if len(items) > 0 else None

    def get_items_in_folder(self, folder: AluFolder) -> list[AluItem]:
        """
        Get all items in a specific folder
        :param folder: An AluFolder object representing the folder to retrieve items from
        :return: A list of AluItem objects in the specified folder
        """
        if folder.guid is None:
            return []
        return self._vault.get_alu_items(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS], p_filter="FolderGUID='" + folder.guid + "'")

    def get_all_folders(self) -> list[AluFolder]:
        """
        Get all folders in the vault
        :return: A list of AluFolder objects representing the folders
        """
        return self._vault.get_alu_folders(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS])

    def get_folder_from_guid(self, guid: str) -> Optional[AluFolder]:
        """
        Get a folder from the vault using its GUID
        :param guid: The GUID of the folder to retrieve
        :return: An AluFolder object matching the GUID, or None if not found
        """
        folders = self._vault.get_alu_folders(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS], p_filter="GUID='" + guid + "'")
        return folders[0] if len(folders) > 0 else None

    def get_folders_in_folder(self, folder: AluFolder) -> list[AluFolder]:
        """
        Get all folders in a specific folder
        :param folder: An AluFolder object representing the folder to retrieve subfolders from
        :return: A list of AluFolder objects in the specified folder
        """
        if folder.guid is None:
            return []
        return self._vault.get_alu_folders(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS], p_filter="ParentFolderGUID='" + folder.guid + "'")

    def get_possible_life_cycle_state_transitions(self, item_revision: AluItemRevision) -> list[AluLifeCycleStateTransition]:
        """
        Get possible life cycle state transitions for an item revision.
        :param item_revision: The AluItemRevision to get transitions for.
        :return: A list of AluLifeCycleStateTransition objects representing valid transitions from the current state.
        """
        if item_revision.lifecycle_state_guid is None:
            return []
        return self._vault.get_alu_life_cycle_state_transitions(
            p_filter=f"LifeCycleStateBeforeGUID = '{item_revision.lifecycle_state_guid}'"
        )

    def change_life_cycle_state(
        self,
        item_revision_list: list[AluItemRevision],
        life_cycle_transition_list: list[AluLifeCycleStateTransition],
    ) -> bool:
        """
        Change the life cycle state of one or more item revisions.
        :param item_revision_list: List of AluItemRevision objects to transition.
        :param life_cycle_transition_list: List of AluLifeCycleStateTransition objects to apply (one per revision).
        :return: True if all state changes were applied successfully.
        """
        if len(item_revision_list) != len(life_cycle_transition_list):
            return False
        return self._vault.add_alu_life_cycle_state_changes(
            item_revision_guids=[r.guid for r in item_revision_list],
            life_cycle_state_transition_guids=[t.guid for t in life_cycle_transition_list],
            life_cycle_state_after_guids=[t.life_cycle_state_after_guid for t in life_cycle_transition_list],
        )

    def get_life_cycle_state_changes_from_item_revision(self, item_revision: AluItemRevision) -> list[AluLifeCycleStateChange]:
        """
        Get all life cycle state changes recorded for an item revision.
        :param item_revision: The AluItemRevision to get state changes for.
        :return: A list of AluLifeCycleStateChange objects.
        """
        if item_revision.guid is None:
            return []
        return self._vault.get_alu_life_cycle_state_changes(
            p_filter=f"ItemRevisionGUID = '{item_revision.guid}'"
        )

    def get_life_cycle_states(self, p_filter: Optional[str] = None) -> list[AluLifeCycleState]:
        """
        Get life cycle states from the vault.
        :param p_filter: Optional filter string.
        :return: A list of AluLifeCycleState objects.
        """
        return self._vault.get_alu_life_cycle_states(p_filter=p_filter)

    def get_life_cycle_definitions(self, p_filter: Optional[str] = None) -> list[AluLifeCycleDefinition]:
        """
        Get life cycle definitions from the vault.
        :param p_filter: Optional filter string.
        :return: A list of AluLifeCycleDefinition objects.
        """
        return self._vault.get_alu_life_cycle_definitions(p_filter=p_filter)
