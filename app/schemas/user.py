from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    username: str = Field(pattern=r"^[a-zA-Z0-9_]+$", min_length=3, max_length=24)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    bio: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
