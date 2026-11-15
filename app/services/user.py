from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidToken, UserDeactivated
from app.models.user import User
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_active_user(self, user_id: int) -> User:

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise InvalidToken

        if not user.is_active:
            raise UserDeactivated

        return user
