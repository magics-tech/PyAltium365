"""Components REST API harness routes."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from test_interface.app.components_patch import ComponentsPatch, PatchError
from test_interface.app.serializers import components_page_to_rows
from test_interface.app.session import HarnessSession


def create_components_router(session: HarnessSession, templates: Jinja2Templates) -> APIRouter:
    """Build components routes bound to a session instance."""
    router = APIRouter(prefix="/api/components", tags=["components"])

    @router.get("/meta")
    async def components_meta() -> dict:
        try:
            return session.get_components_meta()
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.post("/query")
    async def components_query(patch: ComponentsPatch) -> dict:
        try:
            session.apply_components_patch(patch)
            return {
                "success": True,
                "query": session.get_components_query().model_dump(),
                "status": session.status().__dict__,
            }
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except PatchError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/results")
    async def components_results(start: int | None = None, limit: int | None = None) -> dict:
        try:
            page = session.list_components_page(start=start, limit=limit)
            rows = components_page_to_rows(page)
            return {
                "total": page.total,
                "items": [row.model_dump() for row in rows],
                "start": start if start is not None else session.get_components_query().start,
                "limit": limit if limit is not None else session.get_components_query().limit,
            }
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except ConnectionError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @router.get("/find-hrid")
    async def find_hrid(hrid: str) -> dict:
        try:
            record = session.find_component_by_hrid(hrid)
            return {"found": record is not None, "item": record.model_dump() if record else None}
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except ConnectionError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @router.get("/panel-ui", response_class=HTMLResponse)
    async def components_panel_ui(request: Request) -> HTMLResponse:
        try:
            meta = session.get_components_meta()
            return templates.TemplateResponse(
                request,
                "partials/components_builder.html",
                {"meta": meta, "status": session.status()},
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/components_error.html",
                {"error": "Connect a workspace first"},
                status_code=401,
            )

    @router.post("/patch-ui", response_class=HTMLResponse)
    async def components_patch_ui(request: Request, patch: ComponentsPatch) -> HTMLResponse:
        try:
            session.apply_components_patch(patch)
            return templates.TemplateResponse(
                request,
                "partials/components_state.html",
                {
                    "meta": session.get_components_meta(),
                    "error": None,
                },
            )
        except (PermissionError, PatchError) as exc:
            return templates.TemplateResponse(
                request,
                "partials/components_state.html",
                {
                    "meta": session.get_components_meta() if session.workspace else {},
                    "error": str(exc),
                },
                status_code=400,
            )

    @router.get("/results-ui", response_class=HTMLResponse)
    async def components_results_ui(request: Request, start: int = 0, limit: int = 50) -> HTMLResponse:
        try:
            page = session.list_components_page(start=start, limit=limit)
            rows = components_page_to_rows(page)
            return templates.TemplateResponse(
                request,
                "partials/components_results.html",
                {
                    "results": rows,
                    "total": page.total,
                    "start": start,
                    "limit": limit,
                    "workspace_url": session.workspace.workspace_url if session.workspace else "",
                },
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/components_error.html",
                {"error": "Connect a workspace first"},
                status_code=401,
            )

    @router.get("/hrid-ui", response_class=HTMLResponse)
    async def components_hrid_ui(request: Request, hrid: str) -> HTMLResponse:
        try:
            record = session.find_component_by_hrid(hrid)
            return templates.TemplateResponse(
                request,
                "partials/components_hrid_result.html",
                {"hrid": hrid, "record": record, "workspace_url": session.workspace.workspace_url if session.workspace else ""},
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/components_error.html",
                {"error": "Connect a workspace first"},
                status_code=401,
            )

    return router
