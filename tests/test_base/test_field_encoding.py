"""Field encoding unit tests."""

from py_altium365.base.field_encoding import (
    COMPONENTS_API_FIELD_SUFFIX,
    SEARCHASYNC_FIELD_SUFFIX,
    decode_field_name,
    encode_field_name,
    encode_orderby_field,
)


def test_encode_field_name_spaces_and_underscores():
    assert encode_field_name("Update Date") == "Update_20Date"
    assert encode_field_name("test_name") == "test_5Fname"


def test_decode_field_name_round_trip():
    encoded = encode_field_name("Update Date")
    assert decode_field_name(encoded) == "Update Date"


def test_encode_orderby_components_api_descending():
    encoded = encode_orderby_field(
        "Update Date",
        suffix=COMPONENTS_API_FIELD_SUFFIX,
        descending=True,
    )
    assert encoded == f"-Update_20Date{COMPONENTS_API_FIELD_SUFFIX}"


def test_encode_orderby_components_api_ascending():
    encoded = encode_orderby_field(
        "Update Date",
        suffix=COMPONENTS_API_FIELD_SUFFIX,
        descending=False,
    )
    assert encoded == f"Update_20Date{COMPONENTS_API_FIELD_SUFFIX}"


def test_searchasync_suffix_constant():
    assert SEARCHASYNC_FIELD_SUFFIX == "DD420E8DDD8B445E911A0601BB2B6D53"
    assert encode_field_name("test_name") + SEARCHASYNC_FIELD_SUFFIX == "test_5FnameDD420E8DDD8B445E911A0601BB2B6D53"
