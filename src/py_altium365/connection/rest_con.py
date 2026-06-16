"""GET-based REST connection for Altium 365 library APIs."""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from requests import Response, Session

RestAuthMode = Literal["afs", "bearer", "cookies", "alugsid"]


class RestCon:
    """Shared GET transport with Altium session authentication headers."""

    def __init__(
        self,
        session: Session,
        url: str,
        session_guid: str = "",
        *,
        access_token: Optional[str] = None,
        auth_mode: RestAuthMode = "afs",
    ) -> None:
        self._session = session
        self._url = url
        self._session_guid = session_guid
        self._access_token = access_token
        if access_token and auth_mode == "alugsid":
            self._auth_mode: RestAuthMode = "alugsid"
        elif access_token:
            self._auth_mode = "bearer"
        else:
            self._auth_mode = auth_mode

    def _auth_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Altium Designer",
        }
        if self._auth_mode == "alugsid" and self._access_token:
            headers["x-alugsid"] = self._access_token
        elif self._auth_mode == "bearer" and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        elif self._auth_mode == "afs" and self._session_guid:
            headers["Authorization"] = f"AFSSessionID {self._session_guid}"
        return headers

    def _get(self, path: str = "", params: Optional[Dict[str, Any]] = None) -> Response:
        url = self._url if not path else f"{self._url.rstrip('/')}/{path.lstrip('/')}"
        response = self._session.get(url, params=params, headers=self._auth_headers())
        if response.status_code != 200:
            body = response.text[:500]
            raise ConnectionError(f"REST GET failed (HTTP {response.status_code}): {body}")
        return response
