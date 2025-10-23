"""Health check endpoints"""

import logging
from datetime import datetime
from fastapi import APIRouter, status
from app.models.schemas import HealthResponse
from app.core.config import settings
from app.services.llm_service import get_llm_service
from app.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the service is healthy and all dependencies are available"
)
async def health_check():
    """Health check endpoint"""
    
    services_status = {}
    
    # Check LLM service
    try:
        llm_service = get_llm_service()
        llm_healthy = await llm_service.health_check()
        services_status["llm"] = "healthy" if llm_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        services_status["llm"] = "unhealthy"
    
    # Check cache service
    try:
        cache_service = await get_cache_service()
        cache_healthy = await cache_service.health_check()
        services_status["cache"] = "healthy" if cache_healthy else "unhealthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        services_status["cache"] = "unhealthy"
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.utcnow(),
        services=services_status
    )


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Simple ping",
    description="Simple ping endpoint"
)
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}

