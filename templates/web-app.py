from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

WEB_DIST_DIR = Path(__file__).resolve().parents[2] / "web" / "dist"

app = FastAPI()


@app.get("/api/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.api_route(
    "/api",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
async def api_root_not_found() -> None:
    raise HTTPException(status_code=404, detail="API route not found: /api")


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
async def api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail=f"API route not found: /api/{path}")


app.frontend(
    "/",
    directory=WEB_DIST_DIR,
    fallback="index.html",
)
