"""GET-based REST connection for Altium 365 library APIs."""

from __future__ import annotations

from typing import Any, Dict, Optional

from requests import Response, Session


class RestCon:
    """Shared GET transport with Altium session authentication headers."""

    def __init__(self, session: Session, url: str, session_guid: str, host: str) -> None:
        self._session = session
        self._url = url
        self._session_guid = session_guid
        self._host = host

    def _auth_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"AFSSessionID {self._session_guid}",
            "host": self._host,
            "User-Agent": "Altium Designer",
        }

    def _get(self, path: str = "", params: Optional[Dict[str, Any]] = None) -> Response:
        url = self._url if not path else f"{self._url.rstrip('/')}/{path.lstrip('/')}"
        response = self._session.get(url, params=params, headers=self._auth_headers())
        if response.status_code != 200:
            body = response.text[:500]
            raise ConnectionError(f"REST GET failed (HTTP {response.status_code}): {body}")
        return response
