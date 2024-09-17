from sqlalchemy import TIMESTAMP, Column, Integer, String

from .db_connection import Base


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
