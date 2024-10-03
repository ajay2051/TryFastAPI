import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def custom_logging(app: FastAPI):
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """
        Middleware
        :param request:
        :param call_next:
        :return:
        """
        print(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        print(f"Outgoing response: {response.status_code}")
        response.headers["X-Process-Time"] = "0.1"
        return response


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def process_time(request: Request, call_next):
        start_time = time.time()
        print("Before", start_time)
        print(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        processing_time = time.time() - start_time
        print("After", processing_time)
        print(f"Outgoing response: {response.status_code}")
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} {response.status_code} in {processing_time:.2f}"
        print(f"{message}")
        response.headers["X-Process-Time"] = str(processing_time)
        response.headers["Incoming request"] = request.method
        response.headers["Incoming URL"] = request.url.path
        response.headers["Outgoing response"] = response.status_code
        return response

    @app.middleware("http")
    async def authorization(request: Request, call_next):
        if not "Authorization" in request.headers:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"message": "Missing Authorization header"},
            )
        response = await call_next(request)
        return response
