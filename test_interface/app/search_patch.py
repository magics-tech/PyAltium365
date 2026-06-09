"""Pure logic for validating and applying search patches."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field

from py_altium365.connection.json_con_search_async import FacedType, JsonConSearchAsync, SearchDataType


class SortPatch(BaseModel):
    """Sort field patch entry."""

    name: str
    descending: bool = True


class SearchPatch(BaseModel):
    """Patch document applied to an active search."""

    action: Literal[
        "set_content_types",
        "add_term",
        "remove_term",
        "set_range",
        "remove_range",
        "set_wildcard",
        "clear_wildcard",
        "add_sort",
        "clear_sort",
        "clear_all",
    ]
    facet_name: Optional[str] = None
    value: Optional[str] = None
    values: List[str] = Field(default_factory=list)
    content_types: List[str] = Field(default_factory=list)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_inclusive: bool = True
    max_inclusive: bool = True
    faced_type: str = ""
    sort_fields: List[SortPatch] = Field(default_factory=list)
    remove_old: bool = False


class PatchError(Exception):
    """Raised when a search patch cannot be applied."""


def _parse_faced_type(value: str) -> FacedType:
    if not value:
        return FacedType.NO_TYPE
    try:
        return FacedType(value)
    except ValueError as exc:
        raise PatchError(f"Unknown faced type: {value}") from exc


def _facet_index(search: JsonConSearchAsync) -> Dict[Tuple[str, FacedType], bool]:
    index: Dict[Tuple[str, FacedType], bool] = {}
    for name, faced_type in search.get_all_search_names_and_type():
        support_range = any(c.faced_name == name and c.faced_type == faced_type and c.support_range for c in search._search_counters)  # pylint: disable=protected-access
        index[(name, faced_type)] = support_range
    return index


def validate_patch(search: JsonConSearchAsync, patch: SearchPatch) -> None:
    """Validate a patch against current facet metadata."""
    if patch.action == "set_content_types":
        for content_type in patch.content_types:
            try:
                SearchDataType(content_type)
            except ValueError as exc:
                raise PatchError(f"Unknown content type: {content_type}") from exc
        return

    if patch.action in {"add_term", "remove_term", "set_range", "remove_range"}:
        if not patch.facet_name:
            raise PatchError("facet_name is required")
        faced_type = _parse_faced_type(patch.faced_type)
        index = _facet_index(search)
        if (patch.facet_name, faced_type) not in index:
            raise PatchError(f"Unknown facet: {patch.facet_name}")
        if patch.action == "set_range" and not index[(patch.facet_name, faced_type)]:
            raise PatchError(f"Facet does not support range: {patch.facet_name}")
        if patch.action == "set_range":
            if patch.min_value is None or patch.max_value is None:
                raise PatchError("min_value and max_value are required for set_range")
        return

    if patch.action == "set_wildcard" and not patch.value:
        raise PatchError("value is required for set_wildcard")

    if patch.action == "add_sort" and not patch.sort_fields:
        raise PatchError("sort_fields is required for add_sort")


def apply_patch(search: JsonConSearchAsync, patch: SearchPatch) -> None:
    """Apply a validated patch to the search object."""
    validate_patch(search, patch)
    faced_type = _parse_faced_type(patch.faced_type)

    if patch.action == "set_content_types":
        content_types = [SearchDataType(v) for v in patch.content_types]
        search.add_content_search_parameter(content_types, remove_old=patch.remove_old)
        return

    if patch.action == "add_term":
        values: Union[str, List[str]] = patch.values or ([patch.value] if patch.value else [])
        if not values:
            raise PatchError("value or values is required for add_term")
        if not search.add_search_parameter(patch.facet_name or "", values, faced_type, remove_old=patch.remove_old):
            raise PatchError(f"Failed to add term for facet: {patch.facet_name}")
        return

    if patch.action == "remove_term":
        value: Union[str, List[str], None] = patch.values or patch.value
        search.remove_search_parameter(patch.facet_name or "", value, faced_type)
        return

    if patch.action == "set_range":
        if not search.add_search_parameter_range(
            patch.facet_name or "",
            patch.min_value or 0.0,
            patch.max_value or 0.0,
            min_inclusive=patch.min_inclusive,
            max_inclusive=patch.max_inclusive,
            dtype=faced_type,
        ):
            raise PatchError(f"Failed to set range for facet: {patch.facet_name}")
        return

    if patch.action == "remove_range":
        search.remove_search_parameter_range(patch.facet_name or "", faced_type)
        return

    if patch.action == "set_wildcard":
        search.add_search_parameter_wildcard(patch.value or "")
        return

    if patch.action == "clear_wildcard":
        search.remove_search_parameter_wildcard()
        return

    if patch.action == "add_sort":
        search.clear_sort_fields()
        for sort_field in patch.sort_fields:
            search.add_sort_field(sort_field.name, descending=sort_field.descending)
        return

    if patch.action == "clear_sort":
        search.clear_sort_fields()
        return

    if patch.action == "clear_all":
        search.clear_search_parameters()
        search.clear_search_parameters_range()
        search.remove_search_parameter_wildcard()
        search.clear_sort_fields()
        return

    raise PatchError(f"Unsupported action: {patch.action}")
