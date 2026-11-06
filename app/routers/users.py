from fastapi import APIRouter

from app.dependencies.auth import CurrentUser
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> User:

    return current_user
