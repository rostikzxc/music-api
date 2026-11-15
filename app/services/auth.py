import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InvalidCredentials, UserDeactivated, UsernameTaken
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token import TokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserRegister


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_repo = TokenRepository(session)

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

    async def login(self, username: str, password: str) -> Token:
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
        refresh_token = generate_refresh_token()
        hash_refresh_token = hash_token(refresh_token)

        token = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token,
            expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        await self.token_repo.add(token)
        await self.session.commit()

        return Token(access_token=access_token, refresh_token=refresh_token)
