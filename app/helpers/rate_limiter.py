"""Rate limiting utilities"""

import time
import logging
from typing import Dict
from collections import defaultdict
from app.core.exceptions import RateLimitException

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_buckets: Dict[str, list] = defaultdict(list)
        self.hour_buckets: Dict[str, list] = defaultdict(list)
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limits
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if within limits
            
        Raises:
            RateLimitException: If rate limit exceeded
        """
        now = time.time()
        
        # Clean old entries
        self._cleanup_buckets(client_id, now)
        
        # Check minute limit
        minute_requests = len(self.minute_buckets[client_id])
        if minute_requests >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for client {client_id}: {minute_requests} requests in last minute")
            raise RateLimitException(
                f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                details={
                    "limit": self.requests_per_minute,
                    "period": "minute",
                    "current": minute_requests
                }
            )
        
        # Check hour limit
        hour_requests = len(self.hour_buckets[client_id])
        if hour_requests >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded for client {client_id}: {hour_requests} requests in last hour")
            raise RateLimitException(
                f"Rate limit exceeded. Maximum {self.requests_per_hour} requests per hour.",
                details={
                    "limit": self.requests_per_hour,
                    "period": "hour",
                    "current": hour_requests
                }
            )
        
        # Record request
        self.minute_buckets[client_id].append(now)
        self.hour_buckets[client_id].append(now)
        
        return True
    
    def _cleanup_buckets(self, client_id: str, now: float):
        """Remove old entries from buckets"""
        # Clean minute bucket (keep last 60 seconds)
        self.minute_buckets[client_id] = [
            ts for ts in self.minute_buckets[client_id]
            if now - ts < 60
        ]
        
        # Clean hour bucket (keep last 3600 seconds)
        self.hour_buckets[client_id] = [
            ts for ts in self.hour_buckets[client_id]
            if now - ts < 3600
        ]


# Global rate limiter instance
_rate_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    """Get rate limiter instance"""
    return _rate_limiter

