"""
Edify Backend — Common Response Schemas.

Defines standard API response wrappers used across all endpoints.
These enforce the response format defined in the engineering standard:

Success:  { "data": { ... } }
List:     { "data": [...], "meta": { "page": 1, "page_size": 20, "total": 120, "total_pages": 6 } }
Error:    { "error": { "code": "...", "message": "...", "request_id": "..." } }
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ============================================================
# Standard Response Wrappers
# ============================================================


class DataResponse(BaseModel, Generic[T]):
    """Standard single-item response wrapper."""

    data: T


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""

    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Items per page")
    total: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated list response wrapper."""

    data: list[T]
    meta: PaginationMeta


class ErrorDetail(BaseModel):
    """Error detail object."""

    code: str = Field(description="Application-level error code")
    message: str = Field(description="Human-readable error message")
    request_id: str | None = Field(default=None, description="Request tracking ID")


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    error: ErrorDetail


# ============================================================
# Query Parameters
# ============================================================


class PaginationParams(BaseModel):
    """Common pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class SortParams(BaseModel):
    """Common sorting query parameters."""

    sort: str | None = Field(
        default=None,
        description="Sort field. Prefix with '-' for descending (e.g., '-created_at')",
    )

    @property
    def sort_field(self) -> str | None:
        if self.sort is None:
            return None
        return self.sort.lstrip("-")

    @property
    def sort_descending(self) -> bool:
        return self.sort is not None and self.sort.startswith("-")


# ============================================================
# Common Base Schemas
# ============================================================


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.1.0"
