import asyncio

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentials, UserDeactivated, UsernameTaken
from app.core.security import create_access_token, hash_password, verify_password
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

    async def login(self, username: str, password: str) -> str:
        username = username.lower()

        user = await self.user_repo.get_by_username(username)
        if user is None:
            raise InvalidCredentials

        password_ok = await asyncio.to_thread(verify_password, password, user.hashed_password)
        if not password_ok:
            raise InvalidCredentials

        if not user.is_active:
            raise UserDeactivated

        access_token = create_access_token(user.id)

        return access_token
