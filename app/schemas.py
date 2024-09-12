from datetime import datetime

from pydantic import BaseModel


class BooksCreate(BaseModel):
    title: str
    author: str


class BooksResponse(BaseModel):
    id: int
    title: str
    author: str

    # published: bool = True
    # created_at: datetime
    # rating: Optional[int]

    class Config:
        from_attributes = True


class BooksUpdate(BaseModel):
    title: str | None = None
    author: str | None = None


class BookUpdateResponse(BaseModel):
    id: int
    title: str | None = None
    author: str | None = None

    class Config:
        from_attributes = True
