"""
Edify Backend — API Router.

Main v1 router that aggregates all domain routers.
"""

from fastapi import APIRouter

from app.api.v1 import admin, albums, artists, auth, genres, media, search, songs

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(genres.router, tags=["Genres"])
api_router.include_router(artists.router, tags=["Artists"])
api_router.include_router(albums.router, tags=["Albums"])
api_router.include_router(songs.router, tags=["Songs"])
api_router.include_router(search.router, tags=["Search"])
api_router.include_router(admin.router, tags=["Admin"])
api_router.include_router(media.router, tags=["Media"])
