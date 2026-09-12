"""
Password Auth Service
"""
from typing import Optional
from fastapi import Request

from app.core.exceptions import UnauthorizedException, ConflictException, ValidationException
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth.service import AuthService
from app.services.audit.service import AuditService

class PasswordAuthService:
    def __init__(self, user_repo: UserRepository, auth_service: AuthService, audit_service: AuditService):
        self.user_repo = user_repo
        self.auth_service = auth_service
        self.audit_service = audit_service

    async def register(self, email: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None, request: Request | None = None) -> tuple[User, str, str]:
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ConflictException(code="USER_ALREADY_EXISTS", message="A user with this email already exists.")
            
        user = await self.user_repo.create_user(email=email, first_name=first_name, last_name=last_name)
        
        p_hash = hash_password(password)
        await self.user_repo.create_auth_identity(user_id=user.id, provider="password", provider_id=email, password_hash=p_hash)
        
        await self.audit_service.log_action(
            action="USER_REGISTERED",
            entity_type="user",
            entity_id=str(user.id),
            actor_user_id=user.id,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        access_token, refresh_token = await self.auth_service.generate_tokens_for_user(user, request)
        return user, access_token, refresh_token

    async def login(self, email: str, password: str, request: Request | None = None) -> tuple[User, str, str]:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            raise UnauthorizedException(code="AUTH_INVALID_CREDENTIALS", message="Invalid email or password.")
            
        auth_identity = await self.user_repo.get_auth_identity(provider="password", provider_id=email)
        if not auth_identity or not auth_identity.password_hash:
            raise UnauthorizedException(code="AUTH_INVALID_CREDENTIALS", message="Invalid email or password.")
            
        if not verify_password(password, auth_identity.password_hash):
            raise UnauthorizedException(code="AUTH_INVALID_CREDENTIALS", message="Invalid email or password.")
            
        await self.audit_service.log_action(
            action="USER_LOGGED_IN",
            entity_type="user",
            entity_id=str(user.id),
            actor_user_id=user.id,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        access_token, refresh_token = await self.auth_service.generate_tokens_for_user(user, request)
        return user, access_token, refresh_token
