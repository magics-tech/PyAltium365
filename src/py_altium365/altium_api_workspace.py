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
    AluItemRevision,
    AluItemRevisionLink,
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
        if len(items) == 0:
            return None
        return items[0]

    def get_item_revision_from_guid(self, guid: str) -> Optional[AluItemRevision]:
        """
        Get an item revision from the vault using its GUID
        :param guid: The GUID of the item revision to retrieve
        :return: An AluItemRevision object matching the GUID
        """
        revisions = self._vault.get_alu_item_revisions(
            options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS],
            p_filter="GUID='" + guid + "'",
        )
        if len(revisions) == 0:
            return None
        return revisions[0]

    def get_item_revisions_for_item(self, item: AluItem) -> list[AluItemRevision]:
        """
        Get all revisions for a vault item.
        :param item_guid: The GUID of the parent item.
        """
        return self._vault.get_alu_item_revisions(
            options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS],
            p_filter="ItemGUID='" + item.guid + "'",
        )

    def get_latest_item_revision_from_item(self, item: AluItem) -> Optional[AluItemRevision]:
        """
        Get the latest item revision for a given item.
        :param item: The item to get the latest revision for.
        :return: An AluItemRevision object if found, otherwise None.
        """
        revisions = self.get_item_revisions_for_item(item)
        latest = revisions[0]
        for revision in revisions:
            if revision.revision_id > latest.revision_id:
                latest = revision
        return latest

    def get_item_revision_link_from_item_revision(self, item_revision: AluItemRevision, child: bool = True) -> list[AluItemRevisionLink]:
        """
        Get item revision links from a given item revision.
        :param item_revision: The item revision to get links from.
        :param child: Whether to get child links (True) or parent links (False).
        :return: A list of AluItemRevisionLink objects.
        """
        filter = "ParentItemRevisionGUID" if child else "ChildItemRevisionGUID"
        return self._vault.get_alu_item_revision_links(
            p_filter=f"{filter}='{item_revision.guid}'",
        )

    def get_child_item_revisions_from_item_revision(self, item_revision: AluItemRevision) -> list[AluItemRevision]:
        """
        Get child item revisions from a given item revision.
        :param item_revision: The item revision to get child revisions from.
        :return: A list of AluItemRevision objects.
        """
        lin = self.get_item_revision_link_from_item_revision(item_revision, True)
        lout = []
        for li in lin:
            if li.child_item_revision is not None:
                lou = li.child_item_revision
            elif li.child_item_revision_guid is not None:
                lou = self.get_item_revision_from_guid(li.child_item_revision_guid)
            else:
                continue
            if lou is not None:
                lout.append(lou)
        return lout

    def get_parent_item_revisions_from_item_revision(self, item_revision: AluItemRevision) -> list[AluItemRevision]:
        """
        Get parent item revisions from a given item revision.
        :param item_revision: The item revision to get parent revisions from.
        :return: A list of AluItemRevision objects.
        """
        lin = self.get_item_revision_link_from_item_revision(item_revision, False)
        lout = []
        for li in lin:
            lou = self.get_item_revision_from_guid(li.parent_item_revision_guid)
            if lou is not None:
                lout.append(lou)
        return lout

    def get_items_in_folder(self, folder: AluFolder) -> list[AluItem]:
        """
        Get all items in a specific folder
        :param folder: An AluFolder object representing the folder to retrieve items from
        :return: A list of AluItem objects in the specified folder
        """
        if folder.guid is None:
            return []
        items = self._vault.get_alu_items(options=[SoapMethodOption.INCLUDE_ALL_CHILD_OBJECTS], p_filter="FolderGUID='" + folder.guid + "'")
        return [self._bind_vault_item(item) for item in items]

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
