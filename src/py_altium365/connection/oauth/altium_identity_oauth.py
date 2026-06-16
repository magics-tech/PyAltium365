"""Altium 365 browser-style OAuth login via auth.altium.com."""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import httpx

_AUTH_BASE = "https://auth.altium.com"
_TOKEN_URL = f"{_AUTH_BASE}/connect/token"
_JSON_CONTENT_TYPE = "application/json-patch+json"
_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
)
_CONTEXT_COOKIE_RE = re.compile(r"ALU_365_CONTEXT=([^;]+)")
_GSID_RE = re.compile(r"window\.__gsid\s*=\s*'([^']+)'")
_SESSION_ID_RE = re.compile(r"window\.__sessionId\s*=\s*'([^']+)'")
_DEFAULT_WEB_CLIENT_ID = "04189187-35DF-4C54-8941-A6FAB52CEE9B"


@dataclass(frozen=True)
class AltiumOAuthCredentials:
    username: str
    password: str
    workspace_url: str
    workspace_id: Optional[str] = None
    totp_code: Optional[str] = None


@dataclass(frozen=True)
class AltiumOAuthTokens:
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    session_id: Optional[str] = None


def normalize_workspace_url(workspace_url: str) -> str:
    normalized = workspace_url.rstrip("/")
    if normalized.endswith(":443"):
        normalized = normalized[:-4]
    return normalized


def parse_workspace_home_tokens(home_html: str) -> tuple[Optional[str], Optional[str]]:
    """Extract OAuth JWT tokens embedded in the workspace /home page."""
    gsid_match = _GSID_RE.search(home_html)
    session_match = _SESSION_ID_RE.search(home_html)
    return (
        gsid_match.group(1) if gsid_match else None,
        session_match.group(1) if session_match else None,
    )


class AltiumIdentityOAuth:
    """Authenticate against auth.altium.com for workspace REST APIs."""

    def __init__(self, client: Optional[httpx.AsyncClient] = None) -> None:
        self._client = client or httpx.AsyncClient()
        self._apply_browser_headers()
        self._tokens: Optional[AltiumOAuthTokens] = None

    @property
    def client(self) -> httpx.AsyncClient:
        return self._client

    @property
    def tokens(self) -> Optional[AltiumOAuthTokens]:
        return self._tokens

    async def login_with_password(
        self,
        credentials: AltiumOAuthCredentials,
        *,
        service_session_guid: Optional[str] = None,
    ) -> AltiumOAuthTokens:
        del service_session_guid

        workspace_base = normalize_workspace_url(credentials.workspace_url)
        signin_page = await self._client.get(workspace_base, follow_redirects=True, timeout=30)
        callback_return_url = self._signin_callback_return_url(str(signin_page.url))
        if callback_return_url is None:
            raise ConnectionError(
                "Altium OAuth did not redirect to sign-in from the workspace URL"
            )

        await self._prepare_sign_in_context(credentials.username, callback_return_url)
        signin = await self._json_post(
            f"{_AUTH_BASE}/api/account/signIn",
            {
                "userName": credentials.username,
                "password": credentials.password,
                "persistent": True,
                "returnUrl": callback_return_url,
                "visitorId": secrets.token_urlsafe(12),
            },
        )
        next_url = self._resolve_post_signin_url(signin, callback_return_url)
        next_url = await self._complete_two_factor(
            next_url,
            credentials.totp_code,
            callback_return_url,
        )
        await self._follow_authorize_callback(next_url)
        gsid, session_id = await self._load_workspace_tokens(workspace_base)
        if gsid is None:
            raise ConnectionError(
                "Altium OAuth completed but workspace access token (__gsid) was not found"
            )
        self._tokens = AltiumOAuthTokens(access_token=gsid, session_id=session_id)
        return self._tokens

    async def login_with_refresh_token(
        self,
        *,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ) -> AltiumOAuthTokens:
        response = await self._client.post(
            _TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            timeout=30,
        )
        if response.status_code != 200 or "application/json" not in (
            response.headers.get("content-type") or ""
        ):
            raise ConnectionError(
                f"Altium OAuth refresh failed (HTTP {response.status_code}): {response.text[:300]}"
            )
        payload = response.json()
        self._tokens = AltiumOAuthTokens(
            access_token=payload.get("access_token"),
            refresh_token=payload.get("refresh_token", refresh_token),
            expires_in=payload.get("expires_in"),
        )
        return self._tokens

    def _apply_browser_headers(self) -> None:
        self._client.headers["User-Agent"] = _BROWSER_USER_AGENT
        self._client.headers["Accept"] = "application/json, text/plain, */*"

    def _signin_callback_return_url(self, signin_url: str) -> Optional[str]:
        if "/signin" not in signin_url:
            return None
        return_url = parse_qs(urlparse(signin_url).query).get("ReturnUrl", [None])[0]
        if not return_url:
            return None
        return unquote(return_url)

    async def _prepare_sign_in_context(self, username: str, callback_return_url: str) -> None:
        await self._client.get(
            f"{_AUTH_BASE}/api/config",
            params={"returnUrl": callback_return_url},
            timeout=30,
        )
        await self._json_post(
            f"{_AUTH_BASE}/api/userContext/current",
            {
                "returnUrl": callback_return_url,
                "force": False,
                "includeMethods": None,
            },
        )
        await self._json_post(
            f"{_AUTH_BASE}/api/userContext/authenticationMethods",
            {
                "userName": username,
                "returnUrl": callback_return_url,
                "includeMethods": None,
            },
        )

    def _resolve_post_signin_url(self, signin: dict, callback_return_url: str) -> str:
        next_url = (signin.get("returnUrl") or "").strip()
        if not next_url or "/connect/authorize/callback" in next_url:
            return next_url or callback_return_url
        if "/2fa" in next_url:
            return next_url
        return callback_return_url

    async def _load_workspace_tokens(self, workspace_base: str) -> tuple[Optional[str], Optional[str]]:
        home_response = await self._client.get(
            f"{workspace_base}/home",
            follow_redirects=True,
            timeout=30,
        )
        gsid, session_id = parse_workspace_home_tokens(home_response.text)
        if gsid is not None:
            return gsid, session_id
        if self._has_workspace_context_cookie():
            home_response = await self._client.get(
                f"{workspace_base}/home",
                follow_redirects=True,
                timeout=30,
            )
            return parse_workspace_home_tokens(home_response.text)
        await self._bootstrap_workspace_session(workspace_base)
        home_response = await self._client.get(
            f"{workspace_base}/home",
            follow_redirects=True,
            timeout=30,
        )
        return parse_workspace_home_tokens(home_response.text)

    async def _bootstrap_workspace_session(self, workspace_base: str) -> None:
        if self._has_workspace_context_cookie():
            return
        await self._follow_redirects(f"{workspace_base}/home", max_hops=4)

    def _has_workspace_context_cookie(self) -> bool:
        return bool(self._client.cookies.get("ALU_365_CONTEXT"))

    async def _complete_two_factor(
        self,
        next_url: str,
        totp_code: Optional[str],
        callback_return_url: str,
    ) -> str:
        if "/2fa" not in next_url:
            return next_url

        if not totp_code:
            raise ConnectionError(
                "Altium MFA is required for this account. Set ALTIUM_OAUTH_TOTP (or "
                "oauth_totp_code in altium_api_config.yaml), ALTIUM_OAUTH_TOTP_SECRET, "
                "or use OAuth refresh tokens with ALTIUM_CLIENT_ID and ALTIUM_CLIENT_SECRET "
                "from a registered Altium app."
            )

        result = await self._json_post(
            f"{_AUTH_BASE}/api/2fa/challenge",
            {
                "code": totp_code,
                "returnUrl": callback_return_url,
            },
        )
        return result.get("returnUrl", callback_return_url)

    async def _follow_authorize_callback(self, next_url: str) -> None:
        if not next_url:
            raise ConnectionError("Altium OAuth sign-in did not return a continuation URL")
        if next_url.startswith("/"):
            next_url = f"{_AUTH_BASE}{next_url}"
        await self._follow_redirects(next_url, max_hops=16)

    async def _follow_redirects(self, url: str, *, max_hops: int) -> None:
        current = url
        for _ in range(max_hops):
            response = await self._client.get(current, follow_redirects=False, timeout=30)
            if self._context_cookie_from_response(response):
                return
            location = response.headers.get("location")
            if response.status_code not in (301, 302, 303, 307, 308) or not location:
                return
            current = urljoin(current, location)

    def _context_cookie_from_response(self, response: httpx.Response) -> bool:
        set_cookie = response.headers.get("set-cookie", "")
        match = _CONTEXT_COOKIE_RE.search(set_cookie)
        return bool(match and match.group(1))

    async def _json_post(self, url: str, payload: dict) -> dict:
        response = await self._client.post(
            url,
            json=payload,
            headers={"Content-Type": _JSON_CONTENT_TYPE},
            timeout=30,
        )
        return _parse_json_response(response, url)


def _parse_json_response(response: httpx.Response, url: str) -> dict:
    if response.status_code != 200:
        raise ConnectionError(
            f"Altium OAuth request failed for {url} (HTTP {response.status_code}): {response.text[:300]}"
        )
    try:
        payload = response.json()
    except ValueError as exc:
        raise ConnectionError(f"Altium OAuth request returned non-JSON from {url}") from exc
    if not isinstance(payload, dict):
        raise ConnectionError(f"Altium OAuth request returned unexpected payload from {url}")
    return payload
