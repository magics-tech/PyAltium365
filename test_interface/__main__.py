"""Run the PyAltium365 developer harness: python -m test_interface."""

from __future__ import annotations

import uvicorn

from test_interface.app.main import create_app


def main() -> None:
    uvicorn.run(create_app(), host="127.0.0.1", port=8765, log_level="info")


if __name__ == "__main__":
    main()
