"""Authentication routes."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from test_interface.app.serializers import workspace_to_row
from test_interface.app.session import HarnessSession


class LoginRequest(BaseModel):
    username: str
    password: str


def create_auth_router(session: HarnessSession, templates: Jinja2Templates) -> APIRouter:
    """Build auth routes bound to a session instance."""
    router = APIRouter(tags=["auth"])

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        status = session.status()
        workspaces = []
        workspace_name = ""
        workspace_url = ""
        service_urls = []
        if status.portal_active:
            workspaces = [workspace_to_row(ws).model_dump() for ws in session.get_workspaces()]
        if status.workspace_connected:
            workspace_name, workspace_url = session.get_current_workspace_info()
            from test_interface.app.serializers import service_endpoints_to_rows

            service_urls = service_endpoints_to_rows(session.get_service_urls())
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "status": status,
                "workspaces": workspaces,
                "workspace_name": workspace_name,
                "workspace_url": workspace_url,
                "service_urls": service_urls,
            },
        )

    @router.post("/api/login")
    async def api_login(body: LoginRequest) -> dict:
        result = session.login(body.username, body.password)
        status = session.status()
        return {
            "success": result.success,
            "message": result.message,
            "workspace_count": result.workspace_count,
            "status": status.__dict__,
        }

    @router.post("/api/logout")
    async def api_logout() -> dict:
        session.logout()
        return {"success": True, "status": session.status().__dict__}

    @router.get("/api/status")
    async def api_status() -> dict:
        status = session.status()
        workspaces = []
        if status.portal_active:
            workspaces = [workspace_to_row(ws).model_dump() for ws in session.get_workspaces()]
        return {"status": status.__dict__, "workspaces": workspaces}

    @router.post("/login", response_class=HTMLResponse)
    async def login_form(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
    ) -> HTMLResponse:
        result = session.login(username, password)
        status = session.status()
        workspaces = []
        if status.portal_active:
            workspaces = [workspace_to_row(ws).model_dump() for ws in session.get_workspaces()]
        return templates.TemplateResponse(
            request,
            "partials/status.html",
            {"result": result, "status": status, "workspaces": workspaces},
        )

    @router.post("/logout", response_class=HTMLResponse)
    async def logout_form(request: Request) -> HTMLResponse:
        session.logout()
        return templates.TemplateResponse(
            request,
            "partials/login.html",
            {"status": session.status()},
        )

    return router
