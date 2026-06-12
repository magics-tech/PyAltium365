"""TOTP code generation for Altium OAuth two-factor authentication."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

import pyotp

_TOTP_DIGITS = 6
_TOTP_INTERVAL = 30
_TOTP_VALID_WINDOW = 1


def normalize_totp_secret(secret: str) -> str:
    """Normalize a base32 TOTP secret (strip whitespace/dashes, uppercase)."""
    return secret.replace(" ", "").replace("-", "").upper()


def generate_totp_code(
    secret: str,
    *,
    for_time: Optional[Union[datetime, int]] = None,
) -> str:
    """Generate a 6-digit TOTP code for the given authenticator secret."""
    totp = pyotp.TOTP(
        normalize_totp_secret(secret),
        digits=_TOTP_DIGITS,
        interval=_TOTP_INTERVAL,
    )
    if for_time is None:
        return totp.now()
    if isinstance(for_time, datetime):
        if for_time.tzinfo is not None:
            return totp.at(int(for_time.timestamp()))
        return totp.at(for_time)
    return totp.at(for_time)
