"""Components REST API client for GET /components/api/components."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from py_altium365.base.field_encoding import COMPONENTS_API_FIELD_SUFFIX
from py_altium365.connection.rest_list_client import RestListClient, RestListQuery

DEFAULT_COMPONENT_FIELDS = [
    "Id",
    "ItemGUID",
    "HRID",
    "Update Date",
    "Description",
    "Comment",
    "Revision State",
]

_EMPTY_ALTIUM_DATE = datetime(1899, 12, 31)


class ComponentsQuery(RestListQuery):
    """Query parameters for the Components REST list endpoint."""

    fields: List[str] = Field(default_factory=lambda: list(DEFAULT_COMPONENT_FIELDS))
    order_by: List[tuple[str, bool]] = Field(default_factory=lambda: [("Update Date", True)])


class ComponentRecord(BaseModel):
    """Single component row from the Components REST API."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[int] = Field(default=None, alias="Id")
    item_guid: str = Field(default="", alias="ItemGUID")
    hrid: str = Field(default="", alias="HRID")
    update_date: Optional[datetime] = Field(default=None, alias="Update Date")
    description: str = Field(default="", alias="Description")
    comment: str = Field(default="", alias="Comment")
    revision_state: str = Field(default="", alias="Revision State")

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "ComponentRecord":
        return cls.model_validate(row)


class ComponentsListPage(BaseModel):
    """Paginated Components REST response."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    total: int = Field(default=0, alias="Total")
    items: List[ComponentRecord] = Field(default_factory=list, alias="Items")

    @classmethod
    def from_response(cls, payload: Dict[str, Any]) -> "ComponentsListPage":
        total = payload.get("Total", payload.get("total", 0))
        raw_items = payload.get("Items", payload.get("items", []))
        items = [ComponentRecord.from_row(item) if isinstance(item, dict) else item for item in raw_items]
        return cls(total=total, items=items)


def _effective_update_date(record: ComponentRecord) -> Optional[datetime]:
    if record.update_date is None:
        return None
    if record.update_date == _EMPTY_ALTIUM_DATE:
        return None
    return record.update_date


class ComponentsApiClient(RestListClient[ComponentsListPage, ComponentRecord]):
    """Client for the workspace Components REST list API."""

    field_suffix = COMPONENTS_API_FIELD_SUFFIX

    def _parse_page(self, payload: Dict[str, Any]) -> ComponentsListPage:
        return ComponentsListPage.from_response(payload)

    def _page_items(self, page: ComponentsListPage) -> List[ComponentRecord]:
        return page.items

    def list_page(self, query: Optional[ComponentsQuery] = None, **kwargs: Any) -> ComponentsListPage:
        if query is None:
            query = ComponentsQuery(**kwargs) if kwargs else ComponentsQuery()
        elif kwargs:
            query = query.model_copy(update=kwargs)
        return super().list_page(query)

    def list_recent(
        self,
        updated_after: datetime,
        *,
        max_items: Optional[int] = None,
        page_size: int = 50,
    ) -> List[ComponentRecord]:
        """List components updated after a watermark, sorted by Update Date descending."""
        query = ComponentsQuery(order_by=[("Update Date", True)], start=0, limit=page_size)
        results: List[ComponentRecord] = []
        start = 0

        while True:
            if max_items is not None and len(results) >= max_items:
                break

            request_limit = page_size
            if max_items is not None:
                request_limit = min(page_size, max_items - len(results))

            page = self.list_page(query.model_copy(update={"start": start, "limit": request_limit}))
            if not page.items:
                break

            for record in page.items:
                updated = _effective_update_date(record)
                if updated is not None and updated < updated_after:
                    return results

                results.append(record)
                if max_items is not None and len(results) >= max_items:
                    return results

            if len(page.items) < request_limit:
                break
            start += len(page.items)

        return results

    def find_by_hrid(self, hrid: str) -> Optional[ComponentRecord]:
        """Look up a single component by HRID via REST text search."""
        page = self.list_page(ComponentsQuery(text=hrid, limit=50))
        normalized = hrid.strip().lower()
        for record in page.items:
            if record.hrid.strip().lower() == normalized:
                return record
        return None
