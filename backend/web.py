"""Serve the exported Next.js apps from the same origin as the API.

Local `uvicorn --reload` has no `static/` tree, so this is a no-op there.
The production image copies `frontend/out` and `frontend-manager/out` in.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

STATIC = Path(__file__).resolve().parent / "static"


def mount_ui(app: FastAPI) -> None:
    web = STATIC / "web"
    ops = STATIC / "ops"
    if ops.is_dir():
        @app.get("/ops", include_in_schema=False)
        def ops_root():
            return RedirectResponse(url="/ops/")

        app.mount("/ops", StaticFiles(directory=ops, html=True), name="ops")
    if web.is_dir():
        app.mount("/", StaticFiles(directory=web, html=True), name="web")
