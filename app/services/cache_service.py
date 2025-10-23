"""Cache Service - Redis caching layer"""

import json
import logging
import hashlib
from typing import Optional, Any
from redis import asyncio as aioredis
from redis.exceptions import RedisError
from app.core.config import settings
from app.core.exceptions import CacheException

logger = logging.getLogger(__name__)


class CacheService:
    """Service for Redis caching operations"""
    
    def __init__(self):
        self.redis_url = settings.redis_connection_url
        self.default_ttl = settings.CACHE_TTL
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Don't raise exception, allow app to run without cache
            self.redis = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """
        Generate cache key from data
        
        Args:
            prefix: Key prefix
            data: Data to hash
            
        Returns:
            Cache key
        """
        # Convert data to string for hashing
        data_str = json.dumps(data, sort_keys=True)
        hash_value = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss for key: {key}")
            return None
        except RedisError as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        if not self.redis:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            value_str = json.dumps(value)
            await self.redis.setex(key, ttl, value_str)
            logger.debug(f"Cached value for key: {key} with TTL: {ttl}")
            return True
        except RedisError as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return True
        except RedisError as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def get_cached_generation(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> Optional[dict]:
        """
        Get cached code generation result
        
        Args:
            prompt: Generation prompt
            model: Model used
            **kwargs: Additional parameters
            
        Returns:
            Cached result or None
        """
        cache_data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        key = self._generate_key("generation", cache_data)
        return await self.get(key)
    
    async def cache_generation(
        self,
        prompt: str,
        model: str,
        result: dict,
        ttl: Optional[int] = None,
        **kwargs
    ) -> bool:
        """
        Cache code generation result
        
        Args:
            prompt: Generation prompt
            model: Model used
            result: Generation result
            ttl: Time to live
            **kwargs: Additional parameters
            
        Returns:
            True if successful
        """
        cache_data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        key = self._generate_key("generation", cache_data)
        return await self.set(key, result, ttl)
    
    async def health_check(self) -> bool:
        """
        Check if Redis is healthy
        
        Returns:
            True if healthy
        """
        if not self.redis:
            return False
        
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False


# Singleton instance
_cache_service: Optional[CacheService] = None


async def get_cache_service() -> CacheService:
    """Get or create cache service singleton"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        await _cache_service.connect()
    return _cache_service

