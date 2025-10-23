"""
Unified Code Generation Platform - Main Application

Production-ready FastAPI application for AI-powered code generation.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.events import startup_event, shutdown_event
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.api.v1 import api_router

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    await startup_event(app)
    yield
    # Shutdown
    await shutdown_event(app)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered code generation platform using Gemini LLM",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "api": f"{settings.API_V1_PREFIX}/generate_code"
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon endpoint"""
    return JSONResponse(content={}, status_code=204)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        workers=1 if settings.DEBUG else settings.WORKERS
    )

