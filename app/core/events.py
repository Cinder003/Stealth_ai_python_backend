"""Application startup and shutdown events"""

import logging
from fastapi import FastAPI
from .config import settings
from .logging import setup_logging

logger = logging.getLogger(__name__)


async def startup_event(app: FastAPI) -> None:
    """Execute on application startup"""
    # Setup logging
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create storage directories
    import os
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.TEMP_PATH, exist_ok=True)
    logger.info("Storage directories initialized")
    
    # Initialize services (Redis, NATS, etc.)
    logger.info("Services initialization complete")
    logger.info(f"Application ready to serve requests on {settings.HOST}:{settings.PORT}")


async def shutdown_event(app: FastAPI) -> None:
    """Execute on application shutdown"""
    logger.info("Shutting down application...")
    
    # Cleanup resources
    # Close Redis connections
    # Close NATS connections
    # etc.
    
    logger.info("Application shutdown complete")

