"""Tests for component parameter normalization."""

from __future__ import annotations

from py_altium365.component_parameter_utils import merge_altium_parameters, parameters_from_rest_row


def test_merge_prefers_human_readable_suffix() -> None:
    raw = {
        "Value": "1.0E-5",
        "Value_T@x^": "10 µF",
        "Package": "0603",
    }
    merged = merge_altium_parameters(raw)
    assert merged["Value"] == "10 µF"
    assert merged["Package"] == "0603"


def test_parameters_from_rest_row_skips_identity_fields() -> None:
    row = {
        "HRID": "CMP-001",
        "ItemGUID": "guid",
        "Height (max)": "0.9",
        "Height (max)_T@x^": "900 µm",
    }
    params = parameters_from_rest_row(row)
    assert "HRID" not in params
    assert params["Height (max)"] == "900 µm"
