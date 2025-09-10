import redis.asyncio as redis
from typing import Optional
import json
import pickle

from app.core.config import settings


class RedisClient:
    """Redis client for caching and job queue."""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False
        )
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
    
    async def set_json(self, key: str, value: dict, expire: int = 3600):
        """Set JSON value with expiration."""
        if not self.redis:
            await self.connect()
        
        json_value = json.dumps(value)
        await self.redis.set(key, json_value, ex=expire)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value."""
        if not self.redis:
            await self.connect()
        
        value = await self.redis.get(key)
        if value:
            return json.loads(value.decode('utf-8'))
        return None
    
    async def set_object(self, key: str, obj: any, expire: int = 3600):
        """Set pickled object with expiration."""
        if not self.redis:
            await self.connect()
        
        pickled_obj = pickle.dumps(obj)
        await self.redis.set(key, pickled_obj, ex=expire)
    
    async def get_object(self, key: str) -> any:
        """Get pickled object."""
        if not self.redis:
            await self.connect()
        
        value = await self.redis.get(key)
        if value:
            return pickle.loads(value)
        return None
    
    async def delete(self, key: str):
        """Delete key."""
        if not self.redis:
            await self.connect()
        
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.redis:
            await self.connect()
        
        return await self.redis.exists(key)


# Global Redis client instance
redis_client = RedisClient()
