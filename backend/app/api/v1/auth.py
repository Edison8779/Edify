"""
Auth API Router
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.audit import AuditRepository
from app.schemas.auth import AuthResponse, AuthTokensResponse, LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.audit.service import AuditService
from app.services.auth.password import PasswordAuthService
from app.services.auth.service import AuthService
from app.schemas.common import DataResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_password_auth_service(session: Annotated[AsyncSession, Depends(get_db)]) -> PasswordAuthService:
    user_repo = UserRepository(session)
    audit_repo = AuditRepository(session)
    auth_service = AuthService(user_repo)
    audit_service = AuditService(audit_repo)
    return PasswordAuthService(user_repo, auth_service, audit_service)

@router.post("/register", response_model=DataResponse[AuthResponse], status_code=201)
async def register(
    data: UserCreate,
    request: Request,
    auth_service: Annotated[PasswordAuthService, Depends(get_password_auth_service)]
) -> DataResponse[AuthResponse]:
    user, access_token, refresh_token = await auth_service.register(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        request=request
    )
    return DataResponse(
        data=AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=AuthTokensResponse(access_token=access_token, refresh_token=refresh_token)
        )
    )

@router.post("/login", response_model=DataResponse[AuthResponse])
async def login(
    data: LoginRequest,
    request: Request,
    auth_service: Annotated[PasswordAuthService, Depends(get_password_auth_service)]
) -> DataResponse[AuthResponse]:
    user, access_token, refresh_token = await auth_service.login(
        email=data.email,
        password=data.password,
        request=request
    )
    return DataResponse(
        data=AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=AuthTokensResponse(access_token=access_token, refresh_token=refresh_token)
        )
    )

@router.get("/me", response_model=DataResponse[UserResponse])
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> DataResponse[UserResponse]:
    return DataResponse(data=UserResponse.model_validate(current_user))
