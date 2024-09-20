import enum

from sqlalchemy import TIMESTAMP, Boolean, Column, Enum, Integer, String

from .db_connection import Base


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    publisher = Column(String)
    published_date = Column(String)
    page_count = Column(Integer)
    language = Column(String)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"{self.title} {self.author} {self.publisher} {self.published_date} {self.page_count} {self.language}"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
