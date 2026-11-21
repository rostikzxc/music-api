from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_session
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, Token
from app.schemas.user import UserRegister, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister, session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    service = AuthService(session)

    return await service.register(data)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:
    service = AuthService(session)

    return await service.login(form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
async def refresh(
    data: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Token:
    service = AuthService(session)

    return await service.refresh(data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    data: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    service = AuthService(session)

    await service.logout(data.refresh_token)
