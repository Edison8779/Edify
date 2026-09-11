"""
Edify Backend — Model Registry.

Import all models here so Alembic can auto-detect them
for migration generation.

Each model module should be imported as new models are added
in subsequent phases.
"""

from app.models.base import Base, EdifyBase, SoftDeleteMixin

__all__ = [
    "Base",
    "EdifyBase",
    "SoftDeleteMixin",
]

# Phase 1+: Import models here as they are created
# from app.models.user import User
# from app.models.auth_identity import AuthIdentity
# from app.models.refresh_token import RefreshToken
# from app.models.artist import Artist
# from app.models.album import Album
# from app.models.song import Song
# from app.models.genre import Genre
# from app.models.playlist import Playlist
# from app.models.history import PlayHistory
# from app.models.audit_log import AuditLog
