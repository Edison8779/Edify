"""
Edify Backend — FastAPI Application.

Application factory with lifespan management, middleware, and exception handlers.

Request flow:
    HTTP Request
        → Request ID Middleware
        → CORS Middleware
        → Router
        → Schema Validation
        → Service
        → Repository
        → Database
        → Standard Response
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, request_id_ctx, setup_logging
from app.schemas.common import HealthResponse

logger = get_logger(__name__)


# ============================================================
# Application Lifespan
# ============================================================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and shutdown events.

    Startup: initialize logging, verify database connectivity.
    Shutdown: close database connections, cleanup resources.
    """
    # ---- Startup ----
    setup_logging()
    logger.info("edify_starting", environment=settings.app_env)

    # Verify database connection
    try:
        from app.core.database import engine

        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        logger.info("database_connected")
    except Exception:
        logger.exception("database_connection_failed")
        # Don't crash — let health check report the issue

    logger.info("edify_started", port=settings.backend_port)

    yield

    # ---- Shutdown ----
    from app.core.database import engine

    await engine.dispose()
    logger.info("edify_stopped")


# ============================================================
# Application Factory
# ============================================================


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.app_name,
        description="Edify Music Platform — REST API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- Middleware ----
    _register_middleware(application)

    # ---- Exception Handlers ----
    register_exception_handlers(application)

    # ---- Routes ----
    _register_routes(application)

    return application


# ============================================================
# Middleware
# ============================================================


def _register_middleware(app: FastAPI) -> None:
    """Register all middleware on the application."""

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next) -> Response:  # noqa: ANN001
        """
        Assign a unique request ID to every incoming request.

        The ID is:
        1. Set in a context variable for structured logging
        2. Returned in the X-Request-ID response header
        """
        rid = request.headers.get("X-Request-ID", f"req_{uuid.uuid4().hex[:12]}")
        request_id_ctx.set(rid)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = rid

        # Log request completion
        logger.info(
            "request_completed",
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
        )

        return response


# ============================================================
# Routes
# ============================================================


def _register_routes(app: FastAPI) -> None:
    """Register all routes on the application."""

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["System"],
        summary="Health check",
    )
    async def health_check() -> HealthResponse:
        """Check if the API is running and responsive."""
        return HealthResponse()

    # Mount the versioned API router
    app.include_router(api_router)


# ============================================================
# Application Instance
# ============================================================

app = create_app()
