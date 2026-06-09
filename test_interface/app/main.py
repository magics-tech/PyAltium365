"""FastAPI application factory for the test harness."""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from test_interface.app.routes.auth import create_auth_router
from test_interface.app.routes.scenarios import create_scenarios_router
from test_interface.app.routes.components import create_components_router
from test_interface.app.routes.search import create_search_router
from test_interface.app.routes.vault import create_vault_router
from test_interface.app.routes.workspaces import create_workspaces_router
from test_interface.app.session import HarnessSession

TEMPLATES_DIR = Path(__file__).parent / "templates"


def create_app(session: Optional[HarnessSession] = None) -> FastAPI:
    """Create the FastAPI app with an injectable session."""
    harness_session = session or HarnessSession()
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    app = FastAPI(title="PyAltium365 Test Harness", docs_url="/docs", redoc_url=None)
    app.state.session = harness_session  # exposed for tests and debugging

    app.include_router(create_auth_router(harness_session, templates))
    app.include_router(create_workspaces_router(harness_session, templates))
    app.include_router(create_vault_router(harness_session, templates))
    app.include_router(create_search_router(harness_session, templates))
    app.include_router(create_components_router(harness_session, templates))
    app.include_router(create_scenarios_router(harness_session, templates))

    return app


app = create_app()
