from typing import Any, Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()


class BaseError(Exception):
    """
    Base error class for exceptions in this module.
    """
    pass


class InvalidToken(BaseError):
    """
    Error for invalid token or expired token.
    """
    pass


class InsufficientPermission(BaseError):
    """
    Error for insufficient permission.
    """
    pass


def create_exception_handler(status_code: int, message: Any) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BaseError) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content=message
        )

    return exception_handler


def register_all_errors(app: FastAPI):
    """
    Registers all errors here
    :param app:
    :return:
    """
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            message={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(InsufficientPermission,
                              create_exception_handler(status_code=status.HTTP_403_FORBIDDEN, message={"message": "Not enough permissions"}))


@app.exception_handler(500)
async def server_error(app: FastAPI, exception):
    """
    Internal Server Error Handler.
    :param app:
    :param exception:
    :return:
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'message': "OOps something went wrong."},
    )


@app.exception_handler(SQLAlchemyError)
async def database__error(request, exc):
    """
    Database error handler.
    :param request:
    :param exc:
    :return:
    """
    print(str(exc))
    return JSONResponse(
        content={
            "message": "Oops! Something went wrong",
            "error_code": "server_error",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
