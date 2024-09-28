from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, Header, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.auth.routers import auth_router
from app.books.routers import books_router
from app.db_connection import shutdown, startup
from app.custom_exception import InvalidToken, create_exception_handler, InsufficientPermission


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server starting....")
    await startup()
    yield
    await shutdown()
    print("server stopped....")


ver_sion = 'v1'

app = FastAPI(
    title='Books API',
    description='Books API',
    version=ver_sion,
    lifespan=lifespan,
)

origins = [
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(500)
async def server_error(app: FastAPI, exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'message': "OOps something went wrong."},
    )


app.add_exception_handler(InvalidToken, create_exception_handler(status_code=status.HTTP_401_UNAUTHORIZED, message={"message": "Invalid Token"}))
app.add_exception_handler(InsufficientPermission,
                          create_exception_handler(status_code=status.HTTP_403_FORBIDDEN, message={"message": "Not enough permissions"}))


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


app.include_router(books_router, prefix=f'/api/{ver_sion}/books')
app.include_router(auth_router, prefix=f'/api/{ver_sion}/auth')

# Run Project At Specified Port
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
