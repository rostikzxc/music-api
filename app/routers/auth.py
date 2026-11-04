from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_session
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegister, session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    service = UserService(session)

    return await service.register(data)
