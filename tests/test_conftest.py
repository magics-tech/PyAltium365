"""Tests for shared conftest fixtures."""

import os

import pytest


def test_altium_credentials_skips_when_unset(request):
    request.getfixturevalue("monkeypatch").delenv("ALTIUM_USER", raising=False)
    request.getfixturevalue("monkeypatch").delenv("ALTIUM_PASS", raising=False)

    with pytest.raises(pytest.skip.Exception):
        request.getfixturevalue("altium_credentials")


def test_altium_credentials_returns_tuple(request):
    request.getfixturevalue("monkeypatch").setenv("ALTIUM_USER", "user@example.com")
    request.getfixturevalue("monkeypatch").setenv("ALTIUM_PASS", "secret")

    user, password = request.getfixturevalue("altium_credentials")
    assert user == "user@example.com"
    assert password == "secret"
