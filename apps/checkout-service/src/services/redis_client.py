"""
Redis client singleton for caching and session management
"""
import redis
import json
from typing import Optional

class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    def initialize(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis connection"""
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_connect_timeout=5
        )
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value, ex: Optional[int] = None) -> bool:
        """Set a value in Redis"""
        if self.client is None:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.client.set(key, value, ex=ex)
        except:
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis"""
        if self.client is None:
            return None
        try:
            return self.client.get(key)
        except:
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        if self.client is None:
            return False
        try:
            return bool(self.client.delete(key))
        except:
            return False
    
    def incr(self, key: str) -> Optional[int]:
        """Increment a counter"""
        if self.client is None:
            return None
        try:
            return self.client.incr(key)
        except:
            return None

# Global instance
redis_client = RedisClient()
