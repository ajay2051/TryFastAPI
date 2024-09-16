from sqlalchemy import Column, Integer, String, TIMESTAMP

from app.db_connection import Base


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
        return f"Book {self.title} {self.author}"
