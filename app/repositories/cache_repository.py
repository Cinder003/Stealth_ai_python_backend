"""
Cache Repository
Handles Redis cache operations
"""

import json
import pickle
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

import redis
from redis.exceptions import RedisError

from app.core.config import get_settings

settings = get_settings()


class CacheRepository:
    """Repository for Redis cache operations"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=False  # We'll handle encoding/decoding manually
            )
            # Test connection
            self.redis_client.ping()
        except RedisError as e:
            print(f"Redis connection failed: {str(e)}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except RedisError:
            return False
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """Set a value in cache"""
        if not self.is_connected():
            return False
        
        try:
            if serialize:
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value)
                else:
                    serialized_value = str(value)
            else:
                serialized_value = value
            
            if ttl:
                self.redis_client.setex(key, ttl, serialized_value)
            else:
                self.redis_client.set(key, serialized_value)
            
            return True
        except RedisError:
            return False
    
    def get(
        self,
        key: str,
        deserialize: bool = True,
        default: Any = None
    ) -> Any:
        """Get a value from cache"""
        if not self.is_connected():
            return default
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return default
            
            if deserialize:
                try:
                    # Try JSON first
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Fall back to string
                    return value.decode('utf-8')
            else:
                return value
        except RedisError:
            return default
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.is_connected():
            return False
        
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except RedisError:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.is_connected():
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except RedisError:
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for a key"""
        if not self.is_connected():
            return False
        
        try:
            return self.redis_client.expire(key, ttl)
        except RedisError:
            return False
    
    def ttl(self, key: str) -> int:
        """Get TTL for a key"""
        if not self.is_connected():
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except RedisError:
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value"""
        if not self.is_connected():
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except RedisError:
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement a numeric value"""
        if not self.is_connected():
            return None
        
        try:
            return self.redis_client.decrby(key, amount)
        except RedisError:
            return None
    
    def set_hash(
        self,
        key: str,
        field: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set a field in a hash"""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            self.redis_client.hset(key, field, serialized_value)
            
            if ttl:
                self.redis_client.expire(key, ttl)
            
            return True
        except RedisError:
            return False
    
    def get_hash(self, key: str, field: str, default: Any = None) -> Any:
        """Get a field from a hash"""
        if not self.is_connected():
            return default
        
        try:
            value = self.redis_client.hget(key, field)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value.decode('utf-8')
        except RedisError:
            return default
    
    def get_all_hash(self, key: str) -> Dict[str, Any]:
        """Get all fields from a hash"""
        if not self.is_connected():
            return {}
        
        try:
            hash_data = self.redis_client.hgetall(key)
            result = {}
            
            for field, value in hash_data.items():
                field_str = field.decode('utf-8') if isinstance(field, bytes) else field
                try:
                    result[field_str] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field_str] = value.decode('utf-8') if isinstance(value, bytes) else value
            
            return result
        except RedisError:
            return {}
    
    def delete_hash(self, key: str, field: str) -> bool:
        """Delete a field from a hash"""
        if not self.is_connected():
            return False
        
        try:
            result = self.redis_client.hdel(key, field)
            return result > 0
        except RedisError:
            return False
    
    def set_list(
        self,
        key: str,
        values: List[Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set a list in cache"""
        if not self.is_connected():
            return False
        
        try:
            # Clear existing list
            self.redis_client.delete(key)
            
            # Add new values
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value)
                else:
                    serialized_value = str(value)
                
                self.redis_client.rpush(key, serialized_value)
            
            if ttl:
                self.redis_client.expire(key, ttl)
            
            return True
        except RedisError:
            return False
    
    def get_list(
        self,
        key: str,
        start: int = 0,
        end: int = -1
    ) -> List[Any]:
        """Get a list from cache"""
        if not self.is_connected():
            return []
        
        try:
            values = self.redis_client.lrange(key, start, end)
            result = []
            
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value.decode('utf-8'))
            
            return result
        except RedisError:
            return []
    
    def append_list(self, key: str, value: Any) -> bool:
        """Append a value to a list"""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            self.redis_client.rpush(key, serialized_value)
            return True
        except RedisError:
            return False
    
    def prepend_list(self, key: str, value: Any) -> bool:
        """Prepend a value to a list"""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            self.redis_client.lpush(key, serialized_value)
            return True
        except RedisError:
            return False
    
    def get_list_length(self, key: str) -> int:
        """Get length of a list"""
        if not self.is_connected():
            return 0
        
        try:
            return self.redis_client.llen(key)
        except RedisError:
            return 0
    
    def set_set(
        self,
        key: str,
        values: List[Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Set a set in cache"""
        if not self.is_connected():
            return False
        
        try:
            # Clear existing set
            self.redis_client.delete(key)
            
            # Add new values
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value)
                else:
                    serialized_value = str(value)
                
                self.redis_client.sadd(key, serialized_value)
            
            if ttl:
                self.redis_client.expire(key, ttl)
            
            return True
        except RedisError:
            return False
    
    def get_set(self, key: str) -> List[Any]:
        """Get a set from cache"""
        if not self.is_connected():
            return []
        
        try:
            values = self.redis_client.smembers(key)
            result = []
            
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value.decode('utf-8'))
            
            return result
        except RedisError:
            return []
    
    def add_to_set(self, key: str, value: Any) -> bool:
        """Add a value to a set"""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            self.redis_client.sadd(key, serialized_value)
            return True
        except RedisError:
            return False
    
    def remove_from_set(self, key: str, value: Any) -> bool:
        """Remove a value from a set"""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            result = self.redis_client.srem(key, serialized_value)
            return result > 0
        except RedisError:
            return False
    
    def is_in_set(self, key: str, value: Any) -> bool:
        """Check if value is in set"""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            return self.redis_client.sismember(key, serialized_value)
        except RedisError:
            return False
    
    def get_set_size(self, key: str) -> int:
        """Get size of a set"""
        if not self.is_connected():
            return 0
        
        try:
            return self.redis_client.scard(key)
        except RedisError:
            return 0
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        if not self.is_connected():
            return []
        
        try:
            keys = self.redis_client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except RedisError:
            return []
    
    def flush_all(self) -> bool:
        """Flush all keys from cache"""
        if not self.is_connected():
            return False
        
        try:
            self.redis_client.flushall()
            return True
        except RedisError:
            return False
    
    def flush_db(self) -> bool:
        """Flush current database"""
        if not self.is_connected():
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except RedisError:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        if not self.is_connected():
            return {}
        
        try:
            info = self.redis_client.info()
            return {
                'version': info.get('redis_version'),
                'uptime': info.get('uptime_in_seconds'),
                'connected_clients': info.get('connected_clients'),
                'used_memory': info.get('used_memory_human'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except RedisError:
            return {}
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        if not self.is_connected():
            return {}
        
        try:
            info = self.redis_client.info('memory')
            return {
                'used_memory': info.get('used_memory'),
                'used_memory_human': info.get('used_memory_human'),
                'used_memory_rss': info.get('used_memory_rss'),
                'used_memory_peak': info.get('used_memory_peak'),
                'used_memory_peak_human': info.get('used_memory_peak_human')
            }
        except RedisError:
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.is_connected():
            return {}
        
        try:
            info = self.redis_client.info('stats')
            return {
                'total_commands_processed': info.get('total_commands_processed'),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses'),
                'expired_keys': info.get('expired_keys'),
                'evicted_keys': info.get('evicted_keys')
            }
        except RedisError:
            return {}
