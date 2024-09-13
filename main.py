from typing import Optional

from fastapi import FastAPI, Header
from pydantic import BaseModel

from src import books
from src.books.views import books_router

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


app.include_router(books_router)