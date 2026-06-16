"""Generic REST list client base for Altium 365 library APIs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from py_altium365.base.field_encoding import encode_orderby_field
from py_altium365.connection.rest_con import RestCon

PageT = TypeVar("PageT", bound=BaseModel)
RecordT = TypeVar("RecordT")


class RestListQuery(BaseModel):
    """Base query model for REST list endpoints."""

    fields: List[str]
    order_by: List[tuple[str, bool]]
    start: int = 0
    limit: int = 50
    text: str = ""
    tag: str = ""

    def to_params(self, *, field_suffix: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "start": self.start,
            "limit": self.limit,
            "text": self.text,
            "tag": self.tag,
        }
        for field_name in self.fields:
            params.setdefault("fields[]", [])
            if isinstance(params["fields[]"], list):
                params["fields[]"].append(field_name)
        for field_name, descending in self.order_by:
            params.setdefault("orderby[]", [])
            if isinstance(params["orderby[]"], list):
                params["orderby[]"].append(
                    encode_orderby_field(field_name, suffix=field_suffix, descending=descending)
                )
        return params


class RestListClient(RestCon, ABC, Generic[PageT, RecordT]):
    """Shared pagination and query-building for Altium REST list APIs."""

    field_suffix: str

    @abstractmethod
    def _parse_page(self, payload: Dict[str, Any]) -> PageT:
        raise NotImplementedError

    @abstractmethod
    def _page_items(self, page: PageT) -> List[RecordT]:
        raise NotImplementedError

    async def list_page(self, query: RestListQuery) -> PageT:
        response = await self._get(params=query.to_params(field_suffix=self.field_suffix))
        return self._parse_page(response.json())

    async def iter_pages(
        self,
        query: RestListQuery,
        *,
        page_size: int = 50,
        max_items: Optional[int] = None,
    ) -> AsyncIterator[RecordT]:
        start = query.start
        fetched = 0

        while True:
            if max_items is not None and fetched >= max_items:
                return

            limit = page_size
            if max_items is not None:
                limit = min(page_size, max_items - fetched)

            page_query = query.model_copy(update={"start": start, "limit": limit})
            page = await self.list_page(page_query)
            items = self._page_items(page)
            if not items:
                return

            for item in items:
                yield item
                fetched += 1
                if max_items is not None and fetched >= max_items:
                    return

            if len(items) < limit:
                return
            start += len(items)
