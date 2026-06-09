"""Scenario export/import and request trace routes."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from test_interface.app.search_patch import PatchError
from test_interface.app.serializers import ScenarioDocument
from test_interface.app.session import HarnessSession


def create_scenarios_router(session: HarnessSession, templates: Jinja2Templates) -> APIRouter:
    """Build scenario and trace routes bound to a session instance."""
    router = APIRouter(tags=["scenarios"])

    @router.get("/api/scenarios")
    async def export_scenario() -> dict:
        try:
            scenario = session.export_scenario()
            return scenario.model_dump()
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.post("/api/scenarios")
    async def import_scenario(scenario: ScenarioDocument) -> dict:
        try:
            session.import_scenario(scenario)
            return {
                "success": True,
                "meta": session.get_search_meta(),
                "count": session.get_search_count(),
            }
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except PatchError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/api/trace")
    async def get_trace() -> dict:
        entries = session.get_trace()
        return {
            "entries": [
                {
                    "method": entry.method,
                    "url": entry.url,
                    "status_code": entry.status_code,
                    "duration_ms": entry.duration_ms,
                    "timestamp": entry.timestamp,
                    "error": entry.error,
                }
                for entry in entries
            ]
        }

    @router.delete("/api/trace")
    async def clear_trace() -> dict:
        session.clear_trace()
        return {"success": True}

    @router.get("/trace-ui", response_class=HTMLResponse)
    async def trace_ui(request: Request) -> HTMLResponse:
        entries = session.get_trace()
        return templates.TemplateResponse(
            request,
            "partials/trace.html",
            {"entries": entries},
        )

    return router
