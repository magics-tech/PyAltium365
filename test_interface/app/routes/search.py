"""Search builder routes."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from test_interface.app.search_patch import PatchError, SearchPatch
from test_interface.app.session import HarnessSession


class CreateSearchResponse(BaseModel):
    success: bool


def create_search_router(session: HarnessSession, templates: Jinja2Templates) -> APIRouter:
    """Build search routes bound to a session instance."""
    router = APIRouter(prefix="/api/search", tags=["search"])

    @router.post("")
    async def create_search() -> dict:
        try:
            session.create_search()
            return {"success": True, "meta": session.get_search_meta(), "status": session.status().__dict__}
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.patch("")
    async def patch_search(patch: SearchPatch) -> dict:
        try:
            session.apply_patch(patch)
            return {
                "success": True,
                "meta": session.get_search_meta(),
                "count": session.get_search_count(),
                "status": session.status().__dict__,
            }
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except PatchError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.get("/meta")
    async def search_meta() -> dict:
        try:
            return session.get_search_meta()
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.get("/count")
    async def search_count() -> dict:
        try:
            return {"count": session.get_search_count()}
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.get("/results")
    async def search_results(start: int = 0, limit: int = 50) -> dict:
        try:
            results = session.get_results_page(start=start, limit=limit)
            return {"results": [row.model_dump() for row in results], "start": start, "limit": limit}
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        except ConnectionError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @router.post("/create-ui", response_class=HTMLResponse)
    async def create_search_ui(request: Request) -> HTMLResponse:
        try:
            session.create_search()
            meta = session.get_search_meta()
            return templates.TemplateResponse(
                request,
                "partials/search_builder.html",
                {"meta": meta, "count": session.get_search_count(), "status": session.status()},
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/search_error.html",
                {"error": "Connect a workspace first"},
                status_code=401,
            )

    @router.post("/patch-ui", response_class=HTMLResponse)
    async def patch_search_ui(request: Request, patch: SearchPatch) -> HTMLResponse:
        try:
            session.apply_patch(patch)
            return templates.TemplateResponse(
                request,
                "partials/search_state.html",
                {
                    "meta": session.get_search_meta(),
                    "count": session.get_search_count(),
                    "error": None,
                },
            )
        except (PermissionError, PatchError) as exc:
            return templates.TemplateResponse(
                request,
                "partials/search_state.html",
                {
                    "meta": session.get_search_meta() if session.search else {},
                    "count": session.get_search_count() if session.search else 0,
                    "error": str(exc),
                },
                status_code=400,
            )

    @router.get("/results-ui", response_class=HTMLResponse)
    async def search_results_ui(request: Request, start: int = 0, limit: int = 50) -> HTMLResponse:
        try:
            results = session.get_results_page(start=start, limit=limit)
            return templates.TemplateResponse(
                request,
                "partials/search_results.html",
                {"results": results, "start": start, "limit": limit},
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/search_error.html",
                {"error": "Create a search session first"},
                status_code=401,
            )

    return router
