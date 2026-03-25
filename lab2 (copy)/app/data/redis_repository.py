from typing import Optional, Any, Dict, List
from redis_client import RedisClient

class RedisRepository:
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client.client
    
    # String operations
    async def set_string(self, key: str, value: Any) -> bool:
        return await self.redis.set(key, str(value))
    
    async def get_string(self, key: str) -> Optional[str]:
        return await self.redis.get(key)
    
    async def delete_key(self, key: str) -> bool:
        return await self.redis.delete(key) > 0
    
    # Hash operations
    async def hset(self, key: str, field: str, value: Any) -> int:
        return await self.redis.hset(key, field, str(value))
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        return await self.redis.hget(key, field)
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        return await self.redis.hgetall(key)
    
    async def hdel(self, key: str, field: str) -> bool:
        return await self.redis.hdel(key, field) > 0
    
    # List operations
    async def lpush(self, key: str, value: Any) -> int:
        return await self.redis.lpush(key, str(value))
    
    async def rpush(self, key: str, value: Any) -> int:
        return await self.redis.rpush(key, str(value))
    
    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        return await self.redis.lrange(key, start, end)
    
    async def lset(self, key: str, index: int, value: Any) -> bool:
        return await self.redis.lset(key, index, str(value))
    
    async def lrem(self, key: str, value: Any, count: int = 0) -> int:
        return await self.redis.lrem(key, count, str(value))
    
    # Integer operations (using Redis strings for integers)
    async def incr(self, key: str, amount: int = 1) -> int:
        return await self.redis.incrby(key, amount)
    
    async def decr(self, key: str, amount: int = 1) -> int:
        return await self.redis.decrby(key, amount)
    
    # Expiration
    async def expire(self, key: str, seconds: int) -> bool:
        return await self.redis.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        return await self.redis.ttl(key)