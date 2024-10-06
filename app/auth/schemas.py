from typing import List

from pydantic import BaseModel
from pydantic_core.core_schema import ListSchema

from app.models import UserRole


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


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


class LoginData(BaseModel):
    email: str
    password: str


class EmailSchema(BaseModel):
    addresses: List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
