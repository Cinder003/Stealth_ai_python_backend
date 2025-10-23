"""Monitoring and metrics endpoints"""

import logging
from fastapi import APIRouter, status
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

logger = logging.getLogger(__name__)

router = APIRouter()

# Prometheus metrics
generation_requests = Counter(
    'code_generation_requests_total',
    'Total number of code generation requests',
    ['code_type', 'framework', 'status']
)

generation_duration = Histogram(
    'code_generation_duration_seconds',
    'Time spent generating code',
    ['code_type', 'framework']
)

llm_tokens = Counter(
    'llm_tokens_used_total',
    'Total number of LLM tokens used',
    ['model']
)


@router.get(
    "/metrics",
    status_code=status.HTTP_200_OK,
    summary="Prometheus metrics",
    description="Get Prometheus metrics for monitoring"
)
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Application statistics",
    description="Get application statistics and metrics"
)
async def stats():
    """Get application statistics"""
    # TODO: Implement actual statistics gathering
    return {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "average_generation_time": 0.0,
        "cache_hit_rate": 0.0
    }

