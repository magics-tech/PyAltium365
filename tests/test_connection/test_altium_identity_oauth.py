"""Unit tests for Altium OAuth identity login and TOTP handling."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from py_altium365.connection.oauth.altium_identity_oauth import AltiumIdentityOAuth
from py_altium365.connection.oauth.totp import generate_totp_code, normalize_totp_secret


def test_normalize_totp_secret_strips_formatting():
    assert normalize_totp_secret("jbsw y3dp-ehpk3pxp") == "JBSWY3DPEHPK3PXP"


def test_generate_totp_code_known_vector():
    secret = "JBSWY3DPEHPK3PXP"
    for_time = datetime(1970, 1, 1, 0, 0, 59, tzinfo=timezone.utc)
    code = generate_totp_code(secret, for_time=for_time)
    assert code == generate_totp_code(secret, for_time=59)
    assert len(code) == 6


def test_complete_two_factor_skips_when_no_2fa_url(mocker):
    oauth = AltiumIdentityOAuth()
    post = mocker.patch.object(oauth, "_json_post")

    result = oauth._complete_two_factor("https://auth.altium.com/continue")

    assert result == "https://auth.altium.com/continue"
    post.assert_not_called()


def test_complete_two_factor_posts_totp_code(mocker):
    oauth = AltiumIdentityOAuth()
    post = mocker.patch.object(
        oauth,
        "_json_post",
        return_value={"returnUrl": "https://auth.altium.com/done"},
    )

    result = oauth._complete_two_factor(
        "https://auth.altium.com/2fa",
        totp_code="123456",
    )

    assert result == "https://auth.altium.com/done"
    post.assert_called_once_with(
        "https://auth.altium.com/api/2fa/challenge",
        {"code": "123456"},
    )


def test_complete_two_factor_generates_code_from_secret(mocker):
    oauth = AltiumIdentityOAuth()
    post = mocker.patch.object(
        oauth,
        "_json_post",
        return_value={"returnUrl": "https://auth.altium.com/done"},
    )
    generate = mocker.patch(
        "py_altium365.connection.oauth.altium_identity_oauth.generate_totp_code",
        return_value="654321",
    )

    result = oauth._complete_two_factor(
        "https://auth.altium.com/2fa",
        totp_secret="JBSWY3DPEHPK3PXP",
    )

    assert result == "https://auth.altium.com/done"
    generate.assert_called_once_with("JBSWY3DPEHPK3PXP")
    post.assert_called_once_with(
        "https://auth.altium.com/api/2fa/challenge",
        {"code": "654321"},
    )


def test_complete_two_factor_explicit_code_overrides_secret(mocker):
    oauth = AltiumIdentityOAuth()
    post = mocker.patch.object(
        oauth,
        "_json_post",
        return_value={"returnUrl": "https://auth.altium.com/done"},
    )
    generate = mocker.patch(
        "py_altium365.connection.oauth.altium_identity_oauth.generate_totp_code",
    )

    oauth._complete_two_factor(
        "https://auth.altium.com/2fa",
        totp_code="111111",
        totp_secret="JBSWY3DPEHPK3PXP",
    )

    generate.assert_not_called()
    post.assert_called_once_with(
        "https://auth.altium.com/api/2fa/challenge",
        {"code": "111111"},
    )


def test_complete_two_factor_requires_totp_when_skip_rejected(mocker):
    oauth = AltiumIdentityOAuth()
    mocker.patch.object(
        oauth,
        "_json_post",
        side_effect=ConnectionError("Altium OAuth request failed"),
    )

    with pytest.raises(ConnectionError):
        oauth._complete_two_factor("https://auth.altium.com/2fa")
