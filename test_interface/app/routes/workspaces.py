"""Workspace connection routes."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from test_interface.app.serializers import service_endpoints_to_rows, workspace_to_row
from test_interface.app.session import HarnessSession


class ConnectRequest(BaseModel):
    url_or_id: str


def create_workspaces_router(session: HarnessSession, templates: Jinja2Templates) -> APIRouter:
    """Build workspace routes bound to a session instance."""
    router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])

    @router.post("/connect")
    async def connect_workspace(body: ConnectRequest) -> dict:
        try:
            success = session.connect_workspace(body.url_or_id)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        if not success:
            raise HTTPException(status_code=400, detail=session.status().last_error or "Connect failed")
        name, url = session.get_current_workspace_info()
        service_urls = [row.model_dump() for row in service_endpoints_to_rows(session.get_service_urls())]
        return {
            "success": True,
            "workspace": {"name": name, "url": url},
            "service_urls": service_urls,
            "status": session.status().__dict__,
        }

    @router.get("/current")
    async def current_workspace() -> dict:
        try:
            status = session.status()
            if not status.workspace_connected:
                raise HTTPException(status_code=404, detail="No workspace connected")
            name, url = session.get_current_workspace_info()
            service_urls = [row.model_dump() for row in service_endpoints_to_rows(session.get_service_urls())]
            return {
                "workspace": {"name": name, "url": url},
                "service_urls": service_urls,
                "status": status.__dict__,
            }
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.post("/connect-ui", response_class=HTMLResponse)
    async def connect_workspace_ui(request: Request, url_or_id: str) -> HTMLResponse:
        try:
            success = session.connect_workspace(url_or_id)
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/workspace_error.html",
                {"error": "Portal login required"},
                status_code=401,
            )
        if not success:
            return templates.TemplateResponse(
                request,
                "partials/workspace_error.html",
                {"error": session.status().last_error},
                status_code=400,
            )
        name, url = session.get_current_workspace_info()
        service_urls = service_endpoints_to_rows(session.get_service_urls())
        workspaces = [workspace_to_row(ws).model_dump() for ws in session.get_workspaces()]
        return templates.TemplateResponse(
            request,
            "partials/workspace_connected.html",
            {
                "workspace_name": name,
                "workspace_url": url,
                "service_urls": service_urls,
                "workspaces": workspaces,
                "status": session.status(),
            },
        )

    return router
