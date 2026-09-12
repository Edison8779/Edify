"""
Edify Backend — API Router.

Main v1 router that aggregates all domain routers.
Mount domain routers here as they are implemented in subsequent phases.
"""

from __future__ import annotations

from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")

# Phase 2+: Include domain routers here as they are implemented
# from app.api.v1 import auth, users, songs, artists, albums, playlists, library, history, search, admin
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(songs.router, prefix="/songs", tags=["Songs"])
# etc.
