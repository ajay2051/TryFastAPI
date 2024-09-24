from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    username: str
    email: str


class BooksCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BooksResponse(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime
    user: UserBase

    # published: bool = True
    # created_at: datetime
    # rating: Optional[int]

    class Config:
        from_attributes = True


class BooksUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[date] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

    class Config:
        from_attributes = True


class BookUpdateResponse(BaseModel):
    id: int
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    published_date: date | None = None
    page_count: int | None = None
    language: str | None = None

    class Config:
        from_attributes = True
