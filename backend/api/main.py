"""FastAPI app for the Admin/Frontend: ``/api/v1``.

Run (dev):  .venv/bin/uvicorn backend.api.main:app --host 0.0.0.0 --port 8001
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .db import Database
from .routers import admin_settings, auth, catalog, clients, dashboard, editor, public, reports, shares, users
from .security import CSRF_HEADER, resolve_secret_key
from .settings import Settings

API_PREFIX = "/api/v1"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
_TITLES = {400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 409: "Conflict", 410: "Gone",
           422: "Unprocessable Content", 429: "Too Many Requests", 500: "Internal Server Error"}

log = logging.getLogger("hd.api")


def problem(status: int, detail: str, **extra) -> JSONResponse:
    """RFC 9457 problem details; ``detail`` is always a Vietnamese sentence for the UI."""
    body = {"type": "about:blank", "title": _TITLES.get(status, "Error"), "status": status, "detail": detail, **extra}
    return JSONResponse(body, status_code=status, media_type="application/problem+json")


def _field_label(loc: tuple) -> str:
    parts = [str(p) for p in loc if p not in ("body", "query", "path")]
    return ".".join(parts) or "dữ liệu"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        sweeper = None
        if settings.job_recovery:
            from .jobs import RecoverySweeper

            sweeper = RecoverySweeper(application.state.db.session_factory, settings, application.state.secret_key)
            sweeper.start()
        yield
        if sweeper is not None:
            sweeper.stop()

    app = FastAPI(title="Human Design Admin API", version="1.0.0", lifespan=lifespan,
                  docs_url=f"{API_PREFIX}/docs", openapi_url=f"{API_PREFIX}/openapi.json", redoc_url=None)
    app.state.settings = settings
    app.state.secret_key = resolve_secret_key(settings.secret_key, Path(settings.secret_key_file))
    app.state.llm_transport = None  # tests inject a fake OpenAI-compatible transport
    app.state.db = Database(settings.database_url)
    if settings.auto_create_tables:
        app.state.db.create_all()

    if settings.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=True,
                           allow_methods=["*"], allow_headers=["*"])

    @app.middleware("http")
    async def csrf_guard(request: Request, call_next):
        if (request.url.path.startswith(API_PREFIX) and request.method not in SAFE_METHODS
                and not request.headers.get(CSRF_HEADER)):
            return problem(403, "Yêu cầu thiếu header chống giả mạo (CSRF).")
        return await call_next(request)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_request: Request, exc: StarletteHTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "Có lỗi xảy ra."
        return problem(exc.status_code, detail)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, exc: RequestValidationError):
        errors = [{"field": _field_label(tuple(e.get("loc", ()))), "message": e.get("msg", "")} for e in exc.errors()]
        first = errors[0] if errors else {"field": "dữ liệu", "message": ""}
        return problem(422, f"Dữ liệu không hợp lệ ở trường {first['field']}: {first['message']}", errors=errors)

    @app.exception_handler(Exception)
    async def unhandled(_request: Request, exc: Exception):  # pragma: no cover - safety net
        log.exception("unhandled error", exc_info=exc)
        return problem(500, "Máy chủ gặp sự cố, vui lòng thử lại.")

    @app.get(f"{API_PREFIX}/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok", "environment": settings.environment}

    for module in (auth, catalog, clients, editor, shares, reports, dashboard, users, admin_settings, public):
        app.include_router(module.router, prefix=API_PREFIX)
    return app


def __getattr__(name: str):
    # Lazily build the ASGI app so importing this module in tests has no side effects.
    if name == "app":
        global app  # noqa: PLW0603
        app = create_app()
        return app
    raise AttributeError(name)
