"""
Auth Dependencies
"""
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Invalid token payload.")
            
        import uuid
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Invalid token payload.")
            
    except JWTError:
        raise UnauthorizedException(code="AUTH_TOKEN_INVALID", message="Could not validate credentials.")
        
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException(code="USER_NOT_FOUND", message="User not found.")
    if not user.is_active:
        raise UnauthorizedException(code="AUTH_ACCOUNT_DISABLED", message="Inactive user.")
        
    return user

async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_admin:
        raise ForbiddenException()
    return current_user
