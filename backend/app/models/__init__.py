"""
Edify Backend — Model Registry.

Import all models here so Alembic can auto-detect them
for migration generation.
"""

from app.models.base import Base, EdifyBase, SoftDeleteMixin
from app.models.user import User
from app.models.auth_identity import AuthIdentity
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.models.genre import Genre
from app.models.artist import Artist
from app.models.album import Album
from app.models.song import Song
from app.models.song_variant import SongAudioVariant

__all__ = [
    "Base",
    "EdifyBase",
    "SoftDeleteMixin",
    "User",
    "AuthIdentity",
    "RefreshToken",
    "AuditLog",
    "Genre",
    "Artist",
    "Album",
    "Song",
    "SongAudioVariant",
]
