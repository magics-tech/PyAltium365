"""Vault browse routes (read-only)."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from test_interface.app.serializers import build_folder_tree, item_to_row
from test_interface.app.session import HarnessSession


def create_vault_router(session: HarnessSession, templates: Jinja2Templates) -> APIRouter:
    """Build vault routes bound to a session instance."""
    router = APIRouter(prefix="/api/vault", tags=["vault"])

    @router.get("/folders")
    async def list_folders() -> dict:
        try:
            folders = session.list_folders()
            tree = build_folder_tree(folders)
            return {"folders": [node.model_dump() for node in tree]}
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.get("/folders/{guid}/items")
    async def list_items(guid: str) -> dict:
        try:
            items = session.list_items(guid)
            return {"items": [item_to_row(item).model_dump() for item in items]}
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.get("/items/{guid}")
    async def get_item(guid: str) -> dict:
        try:
            item = session.get_item(guid)
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return {"item": item_to_row(item).model_dump()}
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    @router.get("/tree-ui", response_class=HTMLResponse)
    async def vault_tree_ui(request: Request) -> HTMLResponse:
        try:
            folders = session.list_folders()
            tree = build_folder_tree(folders)
            return templates.TemplateResponse(
                request,
                "partials/vault_tree.html",
                {"folders": tree},
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/vault_error.html",
                {"error": "Connect a workspace first"},
                status_code=401,
            )

    @router.get("/folders/{guid}/items-ui", response_class=HTMLResponse)
    async def folder_items_ui(request: Request, guid: str) -> HTMLResponse:
        try:
            items = session.list_items(guid)
            return templates.TemplateResponse(
                request,
                "partials/vault_items.html",
                {"items": [item_to_row(item) for item in items], "folder_guid": guid},
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/vault_error.html",
                {"error": "Connect a workspace first"},
                status_code=401,
            )

    @router.get("/lookup-ui", response_class=HTMLResponse)
    async def lookup_item_ui(request: Request, guid: str) -> HTMLResponse:
        try:
            item = session.get_item(guid)
            return templates.TemplateResponse(
                request,
                "partials/vault_item_detail.html",
                {"item": item_to_row(item) if item else None, "guid": guid},
            )
        except PermissionError:
            return templates.TemplateResponse(
                request,
                "partials/vault_error.html",
                {"error": "Connect a workspace first"},
                status_code=401,
            )

    return router
