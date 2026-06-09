"""DTO serializers for harness API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from py_altium365.connection.components.components_api import ComponentRecord, ComponentsListPage, ComponentsQuery
from py_altium365.connection.json_con_search_async import SearchDataBase
from py_altium365.connection.soapy_con_service_discovery import ServiceEndpoints
from py_altium365.connection.soapy_con_workspace import UserWorkspaceInfo
from py_altium365.connection.vault.soapy_con_vault_base import AluFolder, AluItem


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt is not None else None


class WorkspaceRow(BaseModel):
    workspace_id: int
    name: str
    hosting_url: str
    display_hosting_url: str
    description: str = ""
    is_default: bool = False


class ServiceUrlRow(BaseModel):
    service_kind: str
    url: str


class FolderTreeNode(BaseModel):
    guid: Optional[str] = None
    hrid: Optional[str] = None
    description: Optional[str] = None
    parent_folder_guid: Optional[str] = None
    last_modified_at: Optional[str] = None
    children: List[FolderTreeNode] = Field(default_factory=list)


class ItemRow(BaseModel):
    guid: Optional[str] = None
    hrid: Optional[str] = None
    description: Optional[str] = None
    folder_guid: Optional[str] = None
    last_modified_at: Optional[str] = None
    is_active: bool = False


class ComponentRow(BaseModel):
    id: Optional[int] = None
    item_guid: str = ""
    hrid: str = ""
    update_date: Optional[str] = None
    description: str = ""
    comment: str = ""
    revision_state: str = ""


class OrderByRow(BaseModel):
    name: str
    descending: bool = True


class ComponentsQueryRow(BaseModel):
    fields: List[str] = Field(default_factory=list)
    order_by: List[OrderByRow] = Field(default_factory=list)
    start: int = 0
    limit: int = 50
    text: str = ""
    tag: str = ""


class SearchResultRow(BaseModel):
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    latest_revision: bool = False
    item_guid: Optional[str] = None
    hrid: Optional[str] = None


class SortFieldRow(BaseModel):
    name: str
    descending: bool = True


class ScenarioDocument(BaseModel):
    content_types: List[str] = Field(default_factory=list)
    terms: Dict[str, List[str]] = Field(default_factory=dict)
    ranges: Dict[str, List[float | bool]] = Field(default_factory=dict)
    wildcard: Optional[str] = None
    sort_fields: List[SortFieldRow] = Field(default_factory=list)


def workspace_to_row(ws: UserWorkspaceInfo) -> WorkspaceRow:
    return WorkspaceRow(
        workspace_id=ws.workspace_id,
        name=ws.name,
        hosting_url=ws.hosting_url,
        display_hosting_url=ws.display_hosting_url,
        description=ws.description,
        is_default=ws.is_default,
    )


def service_endpoints_to_rows(endpoints: ServiceEndpoints) -> List[ServiceUrlRow]:
    rows: List[ServiceUrlRow] = []
    for key, value in sorted(endpoints.model_dump().items()):
        if value:
            rows.append(ServiceUrlRow(service_kind=key, url=value))
    return rows


def build_folder_tree(folders: List[AluFolder]) -> List[FolderTreeNode]:
    by_parent: Dict[Optional[str], List[AluFolder]] = {}
    for folder in folders:
        by_parent.setdefault(folder.parent_folder_guid, []).append(folder)

    def attach(parent_guid: Optional[str]) -> List[FolderTreeNode]:
        nodes: List[FolderTreeNode] = []
        for folder in sorted(by_parent.get(parent_guid, []), key=lambda f: (f.hrid or "", f.guid or "")):
            nodes.append(
                FolderTreeNode(
                    guid=folder.guid,
                    hrid=folder.hrid,
                    description=folder.description,
                    parent_folder_guid=folder.parent_folder_guid,
                    last_modified_at=_iso(folder.last_modified_at),
                    children=attach(folder.guid),
                )
            )
        return nodes

    return attach(None)


def item_to_row(item: AluItem) -> ItemRow:
    return ItemRow(
        guid=item.guid,
        hrid=item.hrid,
        description=item.description,
        folder_guid=item.folder_guid,
        last_modified_at=_iso(item.last_modified_at),
        is_active=item.is_active,
    )


def component_record_to_row(record: ComponentRecord) -> ComponentRow:
    return ComponentRow(
        id=record.id,
        item_guid=record.item_guid,
        hrid=record.hrid,
        update_date=_iso(record.update_date),
        description=record.description,
        comment=record.comment,
        revision_state=record.revision_state,
    )


def components_page_to_rows(page: ComponentsListPage) -> List[ComponentRow]:
    return [component_record_to_row(item) for item in page.items]


def components_query_to_row(query: ComponentsQuery) -> ComponentsQueryRow:
    return ComponentsQueryRow(
        fields=list(query.fields),
        order_by=[OrderByRow(name=name, descending=descending) for name, descending in query.order_by],
        start=query.start,
        limit=query.limit,
        text=query.text,
        tag=query.tag,
    )


def search_data_to_row(result: SearchDataBase) -> SearchResultRow:
    return SearchResultRow(
        parameters=dict(result.parameters),
        created_at=_iso(result.created_at),
        latest_revision=result.latest_revision,
        item_guid=result.item_guid or result.parameters.get("GUID") or result.parameters.get("ItemGUID"),
        hrid=result.hrid or result.parameters.get("HRID"),
    )
