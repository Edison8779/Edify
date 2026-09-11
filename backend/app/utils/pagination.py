"""
Edify Backend — Pagination Utilities.

Helpers for computing pagination metadata and building paginated responses.
"""

from __future__ import annotations

import math

from app.schemas.common import PaginatedResponse, PaginationMeta, PaginationParams


def build_pagination_meta(
    *,
    page: int,
    page_size: int,
    total: int,
) -> PaginationMeta:
    """Build pagination metadata from query params and total count."""
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=math.ceil(total / page_size) if page_size > 0 else 0,
    )


def paginated_response(
    *,
    data: list,
    params: PaginationParams,
    total: int,
) -> PaginatedResponse:
    """Build a complete paginated response from data, params, and total count."""
    return PaginatedResponse(
        data=data,
        meta=build_pagination_meta(
            page=params.page,
            page_size=params.page_size,
            total=total,
        ),
    )
