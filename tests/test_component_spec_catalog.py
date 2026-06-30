"""Tests for component spec catalog."""

from __future__ import annotations

from py_altium365.component_spec_catalog import ALL_SPEC_PARAMETER_NAMES, PASSIVES_BASE


def test_passives_base_in_spec_catalog() -> None:
    for name in PASSIVES_BASE:
        assert name in ALL_SPEC_PARAMETER_NAMES
