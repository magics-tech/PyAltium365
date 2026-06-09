"""Shared field-name encoding for Altium 365 search and REST list APIs."""

from __future__ import annotations

SEARCHASYNC_FIELD_SUFFIX = "DD420E8DDD8B445E911A0601BB2B6D53"
COMPONENTS_API_FIELD_SUFFIX = "C623975962814A5FAAD7FA1CD85DA0DB"

ENCODING_DECODING_NAMING = {
    "_5F": "_",
    "_20": " ",
    "_28": "(",
    "_29": ")",
    "_2C": ",",
    "_2D": "-",
    "_2E": ".",
    "_2F": "/",
    "_40": "@",
    "_5B": "[",
    "_5D": "]",
    "_5E": "^",
}


def encode_field_name(name: str) -> str:
    """Encode human-readable field names for Altium API query parameters."""
    encoded = name
    for key, val in ENCODING_DECODING_NAMING.items():
        encoded = encoded.replace(val, key)
    return encoded


def decode_field_name(encoded: str) -> str:
    """Decode Altium API field names back to human-readable form."""
    decoded = encoded
    for key, val in ENCODING_DECODING_NAMING.items():
        decoded = decoded.replace(key, val)
    return decoded


def encode_orderby_field(name: str, *, suffix: str, descending: bool = False) -> str:
    """Encode an order-by field with API-specific suffix and optional descending prefix."""
    encoded = encode_field_name(name) + suffix
    if descending:
        return f"-{encoded}"
    return encoded
