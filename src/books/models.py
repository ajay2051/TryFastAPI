from sqlalchemy import Column, Integer, String

from app.db_connection import Base


class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
