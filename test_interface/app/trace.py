"""Request trace ring buffer for harness debugging."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Deque, List, Optional

import requests


@dataclass(frozen=True)
class TraceEntry:
    method: str
    url: str
    status_code: Optional[int]
    duration_ms: float
    timestamp: str
    error: str = ""


class TracingSession(requests.Session):
    """requests.Session that records recent calls for the harness trace panel."""

    def __init__(self, max_entries: int = 100) -> None:
        super().__init__()
        self._max_entries = max_entries
        self._entries: Deque[TraceEntry] = deque(maxlen=max_entries)

    def request(self, method: str, url: str, **kwargs) -> requests.Response:  # type: ignore[override]
        start = time.perf_counter()
        status_code: Optional[int] = None
        error = ""
        try:
            response = super().request(method, url, **kwargs)
            status_code = response.status_code
            return response
        except Exception as exc:  # noqa: BLE001 — trace all failures
            error = str(exc)
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            self._entries.appendleft(
                TraceEntry(
                    method=method.upper(),
                    url=url,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    error=error,
                )
            )

    def get_trace(self) -> List[TraceEntry]:
        return list(self._entries)

    def clear_trace(self) -> None:
        self._entries.clear()
