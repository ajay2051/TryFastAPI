from typing import Any, Callable

from fastapi.requests import Request
from fastapi.responses import JSONResponse


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
