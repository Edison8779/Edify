"""
Edify Backend — FastAPI Dependencies.

Shared dependencies injected into route handlers via FastAPI's Depends().
"""

from __future__ import annotations

from app.core.database import get_db

__all__ = ["get_db"]

# Phase 2+: Add authentication dependencies here
# from app.dependencies.auth import get_current_user, require_admin
