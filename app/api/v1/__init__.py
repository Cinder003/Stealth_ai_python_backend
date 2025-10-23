"""API v1 package"""

from fastapi import APIRouter
from .routes import health, generate_code, monitoring, figma

api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(generate_code.router, tags=["code-generation"])
api_router.include_router(monitoring.router, tags=["monitoring"])
api_router.include_router(figma.router, tags=["figma"])

__all__ = ["api_router"]

