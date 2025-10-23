"""Observability Service - Langfuse integration for LLM tracing"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

# Langfuse is optional, so we'll handle import errors gracefully
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse not available. Install langfuse package for observability.")


class ObservabilityService:
    """Service for LLM observability and tracing"""
    
    def __init__(self):
        self.enabled = settings.LANGFUSE_ENABLED and LANGFUSE_AVAILABLE
        self.client: Optional[Any] = None
        
        if self.enabled:
            try:
                self.client = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST
                )
                logger.info("Langfuse observability initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse: {e}")
                self.enabled = False
    
    def trace_generation(
        self,
        name: str,
        user_id: str = "anonymous",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Create a trace for code generation
        
        Args:
            name: Trace name
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Trace object or None
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            trace = self.client.trace(
                name=name,
                user_id=user_id,
                metadata=metadata or {}
            )
            return trace
        except Exception as e:
            logger.error(f"Error creating trace: {e}")
            return None
    
    def log_llm_call(
        self,
        trace_id: Optional[str],
        model: str,
        prompt: str,
        response: str,
        tokens_used: int,
        duration_seconds: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log LLM call to Langfuse
        
        Args:
            trace_id: Trace ID
            model: Model used
            prompt: Input prompt
            response: Model response
            tokens_used: Tokens consumed
            duration_seconds: Call duration
            metadata: Additional metadata
        """
        if not self.enabled or not self.client:
            return
        
        try:
            self.client.generation(
                trace_id=trace_id,
                name="code_generation",
                model=model,
                model_parameters={
                    "temperature": metadata.get("temperature", 0.7) if metadata else 0.7,
                    "max_tokens": metadata.get("max_tokens", 8000) if metadata else 8000
                },
                input=prompt,
                output=response,
                usage={
                    "total_tokens": tokens_used
                },
                start_time=datetime.utcnow(),
                metadata=metadata or {}
            )
            logger.debug(f"Logged LLM call to Langfuse: {model}")
        except Exception as e:
            logger.error(f"Error logging to Langfuse: {e}")
    
    def flush(self):
        """Flush pending events to Langfuse"""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Error flushing Langfuse: {e}")


# Singleton instance
_observability_service: Optional[ObservabilityService] = None


def get_observability_service() -> ObservabilityService:
    """Get or create observability service singleton"""
    global _observability_service
    if _observability_service is None:
        _observability_service = ObservabilityService()
    return _observability_service

