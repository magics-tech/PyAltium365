from typing import Optional

import httpx


# pylint: disable=too-few-public-methods
class ConnectionHandler:
    """
    This class is a singleton class that returns an async HTTP client
    """

    def __init__(self):
        self.client = httpx.AsyncClient()

    @staticmethod
    def get_instance() -> httpx.AsyncClient:
        global _connection_handler_instance  # pylint: disable=global-statement
        if _connection_handler_instance is None:
            _connection_handler_instance = ConnectionHandler()
        return _connection_handler_instance.client

    @staticmethod
    def set_instance(client: httpx.AsyncClient):
        global _connection_handler_instance  # pylint: disable=global-statement
        if _connection_handler_instance is None:
            _connection_handler_instance = ConnectionHandler()
        _connection_handler_instance.client = client

    @staticmethod
    async def aclose():
        """Close the underlying HTTP client and reset the singleton."""
        global _connection_handler_instance  # pylint: disable=global-statement
        if _connection_handler_instance is not None:
            await _connection_handler_instance.client.aclose()
            _connection_handler_instance = None


_connection_handler_instance: Optional[ConnectionHandler] = None  # pylint: disable=invalid-name
