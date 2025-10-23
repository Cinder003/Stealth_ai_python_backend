"""Custom exception handlers"""

from typing import Any, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class LLMServiceException(AppException):
    """LLM service related exceptions"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class CodeExtractionException(AppException):
    """Code extraction related exceptions"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class CacheException(AppException):
    """Cache related exceptions"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class RateLimitException(AppException):
    """Rate limiting exceptions"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ValidationException(AppException):
    """Validation exceptions"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions"""
    logger.error(
        f"Application exception: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "details": exc.details
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.detail,
                "details": {}
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "message": "Validation error",
                "details": exc.errors()
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions"""
    logger.exception(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": "Internal server error",
                "details": {}
            }
        }
    )

