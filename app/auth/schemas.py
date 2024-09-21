from pydantic import BaseModel

from app.models import UserRole


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: str | None = None
    role: str = UserRole.USER.value


class UserCreate(UserBase):
    password: str


class AdminUserCreate(BaseModel):
    username: str
    email: str | None = None
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
