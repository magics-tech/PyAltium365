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
        auth_mode = "cookies" if self._oauth_uses_cookies else "afs"
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
