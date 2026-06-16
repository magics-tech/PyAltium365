from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from pydantic_xml import element, wrapped

from py_altium365.connection.soapy_con import SoapMethod, SoapResponse
from py_altium365.connection.vault.soapy_con_vault_base import (
    AluFolder,
    AluItem,
    AluLifeCycleDefinition,
    AluLifeCycleState,
    AluLifeCycleStateChange,
    AluLifeCycleStateTransition,
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


class SoapMethodVaultGetAluLifeCycleStates(
    SoapMethod,
    tag="GetALU_LifeCycleStates",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU life cycle states."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)


class SoapResponseVaultGetAluLifeCycleStates(
    SoapResponse,
    tag="GetALU_LifeCycleStatesResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU life cycle states."""

    records: List[AluLifeCycleState] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapMethodVaultGetAluLifeCycleDefinitions(
    SoapMethod,
    tag="GetALU_LifeCycleDefinitions",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU life cycle definitions."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)


class SoapResponseVaultGetAluLifeCycleDefinitions(
    SoapResponse,
    tag="GetALU_LifeCycleDefinitionsResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU life cycle definitions."""

    records: List[AluLifeCycleDefinition] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapMethodVaultGetAluLifeCycleStateChanges(
    SoapMethod,
    tag="GetALU_LifeCycleStateChanges",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU life cycle state changes."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)


class SoapResponseVaultGetAluLifeCycleStateChanges(
    SoapResponse,
    tag="GetALU_LifeCycleStateChangesResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU life cycle state changes."""

    records: List[AluLifeCycleStateChange] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapMethodVaultGetAluLifeCycleStateTransitions(
    SoapMethod,
    tag="GetALU_LifeCycleStateTransitions",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for getting ALU life cycle state transitions."""

    session_handle: str = element(tag="SessionHandle")
    p_filter: Optional[str] = element(tag="Filter", default=None)


class SoapResponseVaultGetAluLifeCycleStateTransitions(
    SoapResponse,
    tag="GetALU_LifeCycleStateTransitionsResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for getting ALU life cycle state transitions."""

    records: List[AluLifeCycleStateTransition] = wrapped(
        path="Records",
        tag="item",
        default=[],
    )


class SoapMethodVaultAddAluLifeCycleStateChanges(
    SoapMethod,
    tag="AddALU_LifeCycleStateChanges",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP method for adding ALU life cycle state changes."""

    records: List[AluLifeCycleStateChange] = wrapped(
        path="Records",
        entity=element(tag="item"),
        default=[],
    )
    session_handle: str = element(tag="SessionHandle")


class SoapResponseVaultAddAluLifeCycleStateChanges(
    SoapResponse,
    tag="AddALU_LifeCycleStateChangesResponse",
    nsmap={"temp": "http://tempuri.org/"},
    ns="temp",
):
    """SOAP response for adding ALU life cycle state changes."""


class SoapConVault(SoapConVaultBase):
    """SOAP connection class for Altium Vault operations."""

    async def get_alu_items(self, p_filter: Optional[str] = None, options: Optional[List[SoapMethodOption]] = None) -> List[AluItem]:
        """
        Get ALU items from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :param options: A list of options to apply to the query.
        :return: The response containing ALU items.
        """
        if options is None:
            options = []
        response = await self._send_command(
            header=None,
            method=SoapMethodVaultGetAluItems(session_handle=self._altium_workspace.session_guid, p_filter=p_filter, options=options),
            return_method=SoapResponseVaultGetAluItems,
        )
        return response.records

    async def get_alu_life_cycle_states(self, p_filter: Optional[str] = None) -> List[AluLifeCycleState]:
        """
        Get ALU life cycle states from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :return: A list of AluLifeCycleState objects.
        """
        response = await self._send_command(
            header=None,
            method=SoapMethodVaultGetAluLifeCycleStates(session_handle=self._altium_workspace.session_guid, p_filter=p_filter),
            return_method=SoapResponseVaultGetAluLifeCycleStates,
        )
        return response.records

    async def get_alu_life_cycle_definitions(self, p_filter: Optional[str] = None) -> List[AluLifeCycleDefinition]:
        """
        Get ALU life cycle definitions from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :return: A list of AluLifeCycleDefinition objects.
        """
        response = await self._send_command(
            header=None,
            method=SoapMethodVaultGetAluLifeCycleDefinitions(session_handle=self._altium_workspace.session_guid, p_filter=p_filter),
            return_method=SoapResponseVaultGetAluLifeCycleDefinitions,
        )
        return response.records

    async def get_alu_life_cycle_state_changes(self, p_filter: Optional[str] = None) -> List[AluLifeCycleStateChange]:
        """
        Get ALU life cycle state changes from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :return: A list of AluLifeCycleStateChange objects.
        """
        response = await self._send_command(
            header=None,
            method=SoapMethodVaultGetAluLifeCycleStateChanges(session_handle=self._altium_workspace.session_guid, p_filter=p_filter),
            return_method=SoapResponseVaultGetAluLifeCycleStateChanges,
        )
        return response.records

    async def get_alu_life_cycle_state_transitions(self, p_filter: Optional[str] = None) -> List[AluLifeCycleStateTransition]:
        """
        Get ALU life cycle state transitions from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :return: A list of AluLifeCycleStateTransition objects.
        """
        response = await self._send_command(
            header=None,
            method=SoapMethodVaultGetAluLifeCycleStateTransitions(session_handle=self._altium_workspace.session_guid, p_filter=p_filter),
            return_method=SoapResponseVaultGetAluLifeCycleStateTransitions,
        )
        return response.records

    async def add_alu_life_cycle_state_changes(
        self,
        item_revision_guids: List[str],
        life_cycle_state_transition_guids: List[str],
        life_cycle_state_after_guids: List[str],
    ) -> bool:
        """
        Add ALU life cycle state changes to the vault.
        :param item_revision_guids: List of item revision GUIDs.
        :param life_cycle_state_transition_guids: List of life cycle state transition GUIDs.
        :param life_cycle_state_after_guids: List of life cycle state after GUIDs.
        :return: True if the operation was successful.
        """
        if not (len(item_revision_guids) == len(life_cycle_state_transition_guids) == len(life_cycle_state_after_guids)):
            return False
        records = [
            AluLifeCycleStateChange(
                item_revision_guid=item_revision_guids[i],
                life_cycle_state_transition_guid=life_cycle_state_transition_guids[i],
                life_cycle_state_after_guid=life_cycle_state_after_guids[i],
            )
            for i in range(len(item_revision_guids))
        ]
        await self._send_command(
            header=None,
            method=SoapMethodVaultAddAluLifeCycleStateChanges(
                records=records,
                session_handle=self._altium_workspace.session_guid,
            ),
            return_method=SoapResponseVaultAddAluLifeCycleStateChanges,
        )
        return True

    async def get_alu_folders(self, p_filter: Optional[str] = None, options: Optional[List[SoapMethodOption]] = None) -> List[AluFolder]:
        """
        Get ALU folders from the vault.
        :param p_filter: Optional filter string to apply to the query.
        :param options: A list of options to apply to the query.
        :return: The response containing ALU folders.
        """
        if options is None:
            options = []
        response = await self._send_command(
            header=None,
            method=SoapMethodVaultGetAluFolders(session_handle=self._altium_workspace.session_guid, p_filter=p_filter, options=options),
            return_method=SoapResponseVaultGetAluFolders,
        )
        return response.records
