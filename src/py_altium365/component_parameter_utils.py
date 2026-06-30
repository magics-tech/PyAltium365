"""Helpers for normalizing Altium component parameter dicts from search/REST."""

from __future__ import annotations

import re

_HR_SUFFIX = "_T@x^"
_IDENTITY_KEYS = frozenset(
    {
        "Id",
        "HRID",
        "ItemGUID",
        "ItemHRID",
        "Update Date",
        "Description",
        "Comment",
        "Revision State",
        "ContentType",
        "FolderFullPath",
        "LifeCycle",
        "RevisionId",
        "AncestorRevisionGUID",
    }
)


def _is_human_readable_key(key: str) -> bool:
    return key.endswith(_HR_SUFFIX)


def _base_key(key: str) -> str:
    if _is_human_readable_key(key):
        return key[: -len(_HR_SUFFIX)]
    return key


def merge_altium_parameters(*sources: dict[str, object] | None) -> dict[str, str]:
    """Merge parameter dicts; prefer human-readable ``_T@x^`` values over machine values."""
    merged: dict[str, str] = {}
    machine_by_base: dict[str, str] = {}

    for source in sources:
        if not source:
            continue
        for raw_key, raw_value in source.items():
            if raw_value is None:
                continue
            key = str(raw_key).strip()
            if not key or key in _IDENTITY_KEYS:
                continue
            value = str(raw_value).strip()
            if not value:
                continue

            base = _base_key(key)
            if _is_human_readable_key(key):
                merged[base] = value
            elif base not in merged:
                machine_by_base[base] = value

    for base, value in machine_by_base.items():
        merged.setdefault(base, value)

    return merged


def parameters_from_rest_row(row: dict[str, object]) -> dict[str, str]:
    """Extract engineering parameters from a Components REST API row."""
    params: dict[str, object] = {}
    for key, value in row.items():
        if key in _IDENTITY_KEYS or value is None:
            continue
        if isinstance(value, (dict, list)):
            continue
        params[str(key)] = value
    return merge_altium_parameters(params)


# Standard engineering fields requestable via REST ``fields[]``.
STANDARD_ENGINEERING_REST_FIELDS: tuple[str, ...] = (
    "Height (max)",
    "Height",
    "Max/Min Operating Temperature",
    "Operating Temperature",
    "Minimum Temperature",
    "Maximum Temperature",
    "Package",
    "Value",
    "Tolerance",
    "Voltage",
    "Dielectric",
    "ESR",
    "Power (max)",
    "Power Rating",
    "Rated current",
    "DCR",
    "Manufacturer Part Number",
    "Supply voltage",
    "Manufacturer",
    "Pins",
    "Pitch",
)
