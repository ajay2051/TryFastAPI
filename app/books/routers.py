from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app import books, models
from app.auth import auth
from app.books.schemas import BooksResponse, BooksUpdate
from app.db_connection import get_db

books_router = APIRouter(
    tags=['Books']
)


@books_router.post('/create_book/', response_model=BooksResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: books.schemas.BooksCreate, db: Session = Depends(get_db), current_user: auth.schemas.User = Depends(auth.get_current_active_user)):
    new_book = models.Books(**book.__dict__)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@books_router.get('/get_books/', status_code=200)
async def get_all_books(db: Session = Depends(get_db), current_user: auth.schemas.User = Depends(auth.get_current_active_user)):
    all_books = db.query(models.Books).all()
    return all_books


@books_router.get('/get_single_book/{book_id}/', status_code=status.HTTP_200_OK, response_model=BooksUpdate)
def get_single_book(book_id: int, db: Session = Depends(get_db), current_user: auth.schemas.User = Depends(auth.get_current_active_user)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    return book


@books_router.patch('/update_book/{book_id}/', status_code=status.HTTP_200_OK, response_model=BooksUpdate)
async def update_book(book_id: int, book_update: BooksUpdate, db: Session = Depends(get_db), current_user: auth.schemas.User = Depends(auth.get_current_active_user)):
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
async def delete_book(book_id: int, db: Session = Depends(get_db), current_user: auth.schemas.User = Depends(auth.get_current_active_user)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found")
    else:
        db.delete(book)
        db.commit()
    return {"message": "Book deleted successfully"}
