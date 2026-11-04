import asyncio

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UsernameTaken
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserRegister


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, data: UserRegister) -> User:
        username = data.username.lower()

        existing = await self.user_repo.get_by_username(username)
        if existing is not None:
            raise UsernameTaken(username)

        hashed = await asyncio.to_thread(hash_password, data.password)

        user = User(username=username, hashed_password=hashed)

        try:
            await self.user_repo.add(user)
            await self.session.commit()

        except IntegrityError as e:
            await self.session.rollback()
            raise UsernameTaken(username) from e

        return user
