"""Pure logic for validating and applying components query patches."""

from __future__ import annotations

from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

from py_altium365.connection.components.components_api import (
    DEFAULT_COMPONENT_FIELDS,
    ComponentsQuery,
)


class OrderByPatch(BaseModel):
    """Order-by field entry for the components harness."""

    name: str
    descending: bool = True


class ComponentsPatch(BaseModel):
    """Patch document for the components query builder."""

    action: Literal["set_fields", "set_order_by", "set_text", "set_tag", "set_pagination", "reset", "set_query"]
    fields: List[str] = Field(default_factory=list)
    order_by: List[OrderByPatch] = Field(default_factory=list)
    text: Optional[str] = None
    tag: Optional[str] = None
    start: Optional[int] = None
    limit: Optional[int] = None
    query: Optional[ComponentsQuery] = None


class PatchError(Exception):
    """Raised when a components patch cannot be applied."""


def default_components_query() -> ComponentsQuery:
    return ComponentsQuery()


def validate_patch(current: ComponentsQuery, patch: ComponentsPatch) -> None:
    if patch.action == "set_fields" and not patch.fields:
        raise PatchError("fields is required for set_fields")
    if patch.action == "set_order_by" and not patch.order_by:
        raise PatchError("order_by is required for set_order_by")
    if patch.action == "set_pagination":
        if patch.start is None and patch.limit is None:
            raise PatchError("start or limit is required for set_pagination")
    if patch.action == "set_query" and patch.query is None:
        raise PatchError("query is required for set_query")


def apply_patch(current: ComponentsQuery, patch: ComponentsPatch) -> ComponentsQuery:
    validate_patch(current, patch)

    if patch.action == "reset":
        return default_components_query()

    if patch.action == "set_query" and patch.query is not None:
        return patch.query

    if patch.action == "set_fields":
        return current.model_copy(update={"fields": list(patch.fields)})

    if patch.action == "set_order_by":
        order_by: List[Tuple[str, bool]] = [(entry.name, entry.descending) for entry in patch.order_by]
        return current.model_copy(update={"order_by": order_by})

    if patch.action == "set_text":
        return current.model_copy(update={"text": patch.text or ""})

    if patch.action == "set_tag":
        return current.model_copy(update={"tag": patch.tag or ""})

    if patch.action == "set_pagination":
        updates = {}
        if patch.start is not None:
            updates["start"] = patch.start
        if patch.limit is not None:
            updates["limit"] = patch.limit
        return current.model_copy(update=updates)

    raise PatchError(f"Unsupported action: {patch.action}")


def components_query_from_patch(patch: ComponentsPatch) -> ComponentsQuery:
    """Build a one-shot query from a patch without mutating session state."""
    base = default_components_query()
    return apply_patch(base, patch)


DEFAULT_FIELD_OPTIONS = list(DEFAULT_COMPONENT_FIELDS)
