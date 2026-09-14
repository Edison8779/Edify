"""
AuthIdentity Model
"""
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import EdifyBase

if TYPE_CHECKING:
    from app.models.user import User


class AuthIdentity(EdifyBase):
    __tablename__ = "auth_identities"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'password', 'google'
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True) # e.g., email for password, sub for google
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="auth_identities")

    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="uix_auth_identity_provider_provider_id"),
    )
