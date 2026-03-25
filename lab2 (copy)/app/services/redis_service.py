from typing import Optional, Any, Dict, List
from data.redis_repository import RedisRepository

class RedisService:
    def __init__(self, redis_repository: RedisRepository):
        self.repo = redis_repository
    
    # String operations
    async def set_string(self, key: str, value: Any) -> bool:
        return await self.repo.set_string(key, value)
    
    async def get_string(self, key: str) -> Optional[str]:
        return await self.repo.get_string(key)
    
    async def delete_key(self, key: str) -> bool:
        return await self.repo.delete_key(key)
    
    # Hash operations
    async def hset(self, key: str, field: str, value: Any) -> int:
        return await self.repo.hset(key, field, value)
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        return await self.repo.hget(key, field)
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        return await self.repo.hgetall(key)
    
    async def hdel(self, key: str, field: str) -> bool:
        return await self.repo.hdel(key, field)
    
    # List operations
    async def lpush(self, key: str, value: Any) -> int:
        return await self.repo.lpush(key, value)
    
    async def rpush(self, key: str, value: Any) -> int:
        return await self.repo.rpush(key, value)
    
    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        return await self.repo.lrange(key, start, end)
    
    async def lset(self, key: str, index: int, value: Any) -> bool:
        return await self.repo.lset(key, index, value)
    
    async def lrem(self, key: str, value: Any, count: int = 0) -> int:
        return await self.repo.lrem(key, value, count)
    
    # Integer operations
    async def increment(self, key: str, amount: int = 1) -> int:
        return await self.repo.incr(key, amount)
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        return await self.repo.decr(key, amount)
    
    # Expiration
    async def expire(self, key: str, seconds: int) -> bool:
        return await self.repo.expire(key, seconds)
    
    async def ttl(self, key: str) -> int:
        return await self.repo.ttl(key)