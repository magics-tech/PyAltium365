from typing import Generic, Type, TypeVar

import httpx
from pydantic import BaseModel


class JsonRequest(BaseModel):
    """Base class for SOAP method."""


RequestT = TypeVar("RequestT", bound=JsonRequest)


class JsonBase(BaseModel, Generic[RequestT]):
    """Base class for JSON method."""

    request: RequestT


class JsonReturn(BaseModel):
    """Base class for JSON return."""


class JsonCon:
    """Base class for JSON connection."""

    def __init__(self, client: httpx.AsyncClient, url: str, session_guid: str, host: str):
        """
        Initialize the JsonCon object
        :param client: The async HTTP client
        :param url: The URL to send the JSON request to
        :param session_guid: The session GUID
        :param host: The host for the host parameter
        """
        self._client: httpx.AsyncClient = client
        self._url: str = url
        self._session_guid: str = session_guid
        self._host: str = host

    ReturnMethodT = TypeVar("ReturnMethodT", bound=JsonReturn)

    async def _send_command(self, request: JsonRequest, return_method: Type[ReturnMethodT]) -> ReturnMethodT:
        headers = {
            "Accept": "application/json",
            "Authorization": f"AFSSessionID {self._session_guid}",
            "host": self._host,
            "content-type": "application/json; charset=utf-8",
            "User-Agent": "Altium Designer",
        }

        json_data = JsonBase(request=request).json(by_alias=True)

        response = await self._client.request(
            "REPORT", self._url, content=json_data.encode("utf-8"), headers=headers,
            timeout=httpx.Timeout(connect=10.0, read=120.0, write=10.0, pool=10.0),
        )

        if response.status_code != 200:
            body = response.text[:500]
            raise ConnectionError(
                f"Failed to send JSON command (HTTP {response.status_code}): {body}"
            )

        return return_method.parse_raw(response.content.decode("utf-8-sig"))
