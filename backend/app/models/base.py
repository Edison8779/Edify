"""
Edify Backend — Base SQLAlchemy Model.

All models inherit from EdifyBase which provides:
- UUID primary key (auto-generated)
- created_at / updated_at timestamps

Models requiring soft-delete inherit SoftDeleteMixin for `deleted_at`.

Uses modern SQLAlchemy 2.x style with Mapped[] and mapped_column().
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all Edify models."""

    pass


class EdifyBase(Base):
    """
    Abstract base model with UUID primary key and timestamps.

    All Edify database models should inherit from this class.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"


class SoftDeleteMixin:
    """
    Mixin for models that support soft-delete.

    Instead of DELETE FROM table, set deleted_at = now().
    Query filters should exclude rows where deleted_at IS NOT NULL.
    Admin can restore by setting deleted_at = NULL.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
