from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.db_connection import get_db
from src.books import models
from src.books.schemas import BooksCreate, BooksResponse, BooksUpdate

books_router = APIRouter(
    prefix="/books",
    tags=['Books']
)


@books_router.post('/create_book/', response_model=BooksResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BooksCreate, db: Session = Depends(get_db)) -> BooksResponse:
    new_book = models.Books(**book.__dict__)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@books_router.get('/get_books/', status_code=200)
async def get_all_books(db: Session = Depends(get_db)):
    all_books = db.query(models.Books).all()
    return all_books


@books_router.get('/get_single_book/{book_id}/', status_code=status.HTTP_200_OK)
def get_single_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    return book


@books_router.patch('/update_book/{book_id}/', status_code=status.HTTP_200_OK)
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


@books_router.delete('/delete_book{book_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    else:
        db.delete(book)
        db.commit()
    return {"message": "Book deleted successfully"}
