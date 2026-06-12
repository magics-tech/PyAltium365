from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic_xml import element, wrapped

from py_altium365.connection.soapy_con import SoapMethod, SoapResponse
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluFolder,
    AluItem,
    AluItemRevision,
    AluItemRevisionLink,
    SoapConVaultBase,
    SoapMethodOption,
)

if TYPE_CHECKING:
    from py_altium365.altium_api_workspace import AltiumApiWorkspace  # noqa: F401


class SoapMethodVaultGetAluItems(
    SoapMethod,
    tag="GetALU_Items",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU items."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)
    options: List[SoapMethodOption] = wrapped(
        path="Options",
        entity=element(tag="item"),
        default=[],
    )


class SoapResponseVaultGetAluItems(
    SoapResponse,
    tag="GetALU_ItemsResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU items."""

    records: List[AluItem] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapMethodVaultGetAluFolders(
    SoapMethod,
    tag="GetALU_Folders",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU folders."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)
    options: List[SoapMethodOption] = wrapped(
        path="Options",
        entity=element(tag="item"),
        default=[],
    )


class SoapResponseVaultGetAluFolders(
    SoapResponse,
    tag="GetALU_FoldersResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU folders."""

    records: List[AluFolder] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapMethodVaultGetAluItemRevisions(
    SoapMethod,
    tag="GetALU_ItemRevisions",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU item revisions."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)
    options: List[SoapMethodOption] = wrapped(
        path="Options",
        entity=element(tag="item"),
        default=[],
    )


class SoapResponseVaultGetAluItemRevisions(
    SoapResponse,
    tag="GetALU_ItemRevisionsResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU item revisions."""

    records: List[AluItemRevision] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapMethodVaultGetAluItemRevisionLinks(
    SoapMethod,
    tag="GetALU_ItemRevisionLinks",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU item revision links."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)
    options: List[SoapMethodOption] = wrapped(
        path="Options",
        entity=element(tag="item"),
        default=[],
    )


class SoapResponseVaultGetAluItemRevisionLinks(
    SoapResponse,
    tag="GetALU_ItemRevisionLinksResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU item revision links."""

    records: List[AluItemRevisionLink] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapConVault(SoapConVaultBase):
    """SOAP connection class for Altium Vault operations."""

    def get_alu_items(self, p_filter: Optional[str] = None, options: Optional[List[SoapMethodOption]] = None) -> List[AluItem]:
        """
        Get ALU items from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :param options: A list of options to apply to the query.
        :return: The response containing ALU items.
        """
        if options is None:
            options = []
        response = self._send_command(
            header=None,
            method=SoapMethodVaultGetAluItems(session_handle=self._altium_workspace.session_guid, p_filter=p_filter, options=options),
            return_method=SoapResponseVaultGetAluItems,
        )
        return response.records

    def get_alu_item_revisions(self, p_filter: Optional[str] = None, options: Optional[List[SoapMethodOption]] = None) -> List[AluItemRevision]:
        """
        Get ALU item revisions from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :param options: A list of options to apply to the query.
        :return: The response containing ALU item revisions.
        """
        if options is None:
            options = []
        response = self._send_command(
            header=None,
            method=SoapMethodVaultGetAluItemRevisions(session_handle=self._altium_workspace.session_guid, p_filter=p_filter, options=options),
            return_method=SoapResponseVaultGetAluItemRevisions,
        )
        return response.records

    def get_alu_item_revision_links(self, p_filter: Optional[str] = None, options: Optional[List[SoapMethodOption]] = None) -> List[AluItemRevisionLink]:
        """
        Get ALU item revision links from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :param options: A list of options to apply to the query.
        :return: The response containing ALU item revision links.
        """
        if options is None:
            options = []
        response = self._send_command(
            header=None,
            method=SoapMethodVaultGetAluItemRevisionLinks(session_handle=self._altium_workspace.session_guid, p_filter=p_filter, options=options),
            return_method=SoapResponseVaultGetAluItemRevisionLinks,
        )
        return response.records

    def get_alu_folders(self, p_filter: Optional[str] = None, options: Optional[List[SoapMethodOption]] = None) -> List[AluFolder]:
        """
        Get ALU folders from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :param options: A list of options to apply to the query.
        :return: The response containing ALU folders.
        """
        if options is None:
            options = []
        response = self._send_command(
            header=None,
            method=SoapMethodVaultGetAluFolders(session_handle=self._altium_workspace.session_guid, p_filter=p_filter, options=options),
            return_method=SoapResponseVaultGetAluFolders,
        )
        return response.records
