from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.database import engine, Base
from app.exceptions import AppException
from app.models import *  # noqa: F401, F403 -- ensures all models are registered with Base
from app.routers import garments, materials, attributes, suppliers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Fashion PLM API",
    description="Fashion Product Lifecycle Management System",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "detail": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "detail": str(exc),
        },
    )


# Routers
app.include_router(garments.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(attributes.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
