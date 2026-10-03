from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import (
    http_error_handler,
    service_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)
from app.repository import StudentRepository
from app.routes import router
from app.service import ServiceError

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository = StudentRepository()
    repository.load()
    app.state.repository = repository
    yield


app = FastAPI(title="Управление студентами", lifespan=lifespan)

app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

app.include_router(router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
