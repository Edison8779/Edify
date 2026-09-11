"""
Edify Backend — Exception Handling.

Defines application-level exceptions and the global exception handler.

Standard error response format:
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message.",
    "request_id": "req_..."
  }
}

Never expose: SQL queries, database errors, stack traces, filesystem paths,
or internal service details to clients.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger, request_id_ctx

logger = get_logger(__name__)


# ============================================================
# Application Exceptions
# ============================================================


class EdifyException(Exception):
    """Base exception for all Edify application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.headers = headers
        super().__init__(message)


class NotFoundException(EdifyException):
    """Resource not found (404)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=404)


class UnauthorizedException(EdifyException):
    """Authentication failed (401)."""

    def __init__(
        self,
        code: str = "AUTH_UNAUTHORIZED",
        message: str = "Authentication required.",
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(EdifyException):
    """Insufficient permissions (403)."""

    def __init__(
        self,
        code: str = "PERMISSION_DENIED",
        message: str = "You do not have permission to perform this action.",
    ) -> None:
        super().__init__(code=code, message=message, status_code=403)


class ConflictException(EdifyException):
    """Resource conflict (409)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=409)


class ValidationException(EdifyException):
    """Business-rule validation failure (422)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=422)


# ============================================================
# Error Response Builder
# ============================================================


def _build_error_response(
    status_code: int,
    code: str,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """Build a standardized error JSON response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id_ctx.get(),
            },
        },
        headers=headers,
    )


# ============================================================
# Global Exception Handlers
# ============================================================


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(EdifyException)
    async def edify_exception_handler(
        request: Request,
        exc: EdifyException,
    ) -> JSONResponse:
        logger.warning(
            "application_error",
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url.path),
        )
        return _build_error_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            headers=exc.headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        logger.warning(
            "http_error",
            status_code=exc.status_code,
            detail=str(exc.detail),
            path=str(request.url.path),
        )
        return _build_error_response(
            status_code=exc.status_code,
            code="HTTP_ERROR",
            message=str(exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "validation_error",
            errors=str(exc.errors()),
            path=str(request.url.path),
        )
        # Provide a user-friendly message while keeping details structured
        first_error = exc.errors()[0] if exc.errors() else {}
        field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        msg = first_error.get("msg", "Invalid input.")

        return _build_error_response(
            status_code=422,
            code="VALIDATION_ERROR",
            message=f"{field}: {msg}" if field else msg,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        # Log the full exception for debugging — never expose to client
        logger.exception(
            "unhandled_error",
            error_type=type(exc).__name__,
            path=str(request.url.path),
        )
        return _build_error_response(
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred.",
        )
