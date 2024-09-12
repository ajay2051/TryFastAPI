from typing import Optional, List

from fastapi import FastAPI, Header, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from app import models
from app.db_connection import get_db
from app.models import Books
from app.schemas import BooksResponse, BooksCreate, BooksUpdate

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": " Hello World"}


@app.get('/greet/{name}/')
def greet_name(age: Optional[int], name: str = 'ajay') -> dict:
    """
    If we remove {name} from @app.get('/greet/{name}') then append url {name} with query params.
    age is added as query params
    :param age:
    :param name:
    :return: message
    """
    return {"message": f"Hello {name}. Age: {age}"}


class BookCreateModel(BaseModel):
    title: str
    author: str


# @app.post('/create_book')
# async def create_book(book_data: BookCreateModel):
#     return {
#         "title": book_data.title,
#         "author": book_data.author,
#     }


@app.get('/get_headers', status_code=200)
async def get_headers(
        accept: str = Header(None),
        content_type: str = Header(None),
        user_agent: str = Header(None),
        host: str = Header(None),
):
    """
    This function creates headers.
    :param host:
    :param user_agent:
    :param accept:
    :param content_type:
    :return: request_headers dictionary
    """
    request_headers = {}
    request_headers['Accept'] = accept
    request_headers['Content-Type'] = content_type
    request_headers['User-Agent'] = user_agent
    request_headers['Host'] = host
    return request_headers


@app.post('/create_book/', response_model=BooksResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BooksCreate, db: Session = Depends(get_db)) -> BooksResponse:
    new_book = models.Books(**book.__dict__)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@app.get('/get_books/', status_code=200)
async def get_all_books(db: Session = Depends(get_db)):
    all_books = db.query(models.Books).all()
    return all_books


@app.get('/get_single_book/{book_id}/', status_code=status.HTTP_200_OK)
def get_single_book(book_id: int, db : Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    return book


@app.patch('/update_book/{book_id}/', status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book_update: BooksUpdate, db: Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@app.delete('/delete_book{book_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    else:
        db.delete(book)
        db.commit()
    return {"message": "Book deleted successfully"}
