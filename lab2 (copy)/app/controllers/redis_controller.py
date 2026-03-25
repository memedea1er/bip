from fastapi import APIRouter, HTTPException
from services.redis_service import RedisService
from models import (
    RedisKeyOperation, RedisHashOperation, RedisListOperation,
    RedisExpireOperation, RedisIncrementOperation
)

class RedisController:
    def __init__(self, redis_service: RedisService):
        self.service = redis_service
        self.router = APIRouter(prefix="/redis", tags=["redis"])
        self._register_routes()
    
    def _register_routes(self):
        # String operations
        self.router.post("/string/{key}")(self.set_string)
        self.router.get("/string/{key}")(self.get_string)
        
        # Hash operations
        self.router.post("/hash/{key}/field/{field}")(self.hset)
        self.router.get("/hash/{key}/field/{field}")(self.hget)
        self.router.get("/hash/{key}")(self.hgetall)
        self.router.delete("/hash/{key}/field/{field}")(self.hdel)
        
        # List operations
        self.router.post("/list/{key}/left")(self.lpush)
        self.router.post("/list/{key}/right")(self.rpush)
        self.router.get("/list/{key}")(self.lrange)
        self.router.put("/list/{key}/index/{index}")(self.lset)
        self.router.delete("/list/{key}/value/{value}")(self.lrem)
        
        # Integer operations
        self.router.post("/int/{key}/increment")(self.increment)
        
        # Key operations
        self.router.delete("/key/{key}")(self.delete_key)
        self.router.post("/key/{key}/expire")(self.expire)
        self.router.get("/key/{key}/ttl")(self.ttl)
    
    async def set_string(self, key: str, operation: RedisKeyOperation):
        success = await self.service.set_string(key, operation.value)
        return {"success": success, "key": key}
    
    async def get_string(self, key: str):
        value = await self.service.get_string(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": value}
    
    async def hset(self, key: str, field: str, operation: RedisHashOperation):
        result = await self.service.hset(key, field, operation.value)
        return {"success": True, "key": key, "field": field}
    
    async def hget(self, key: str, field: str):
        value = await self.service.hget(key, field)
        if value is None:
            raise HTTPException(status_code=404, detail="Field not found")
        return {"key": key, "field": field, "value": value}
    
    async def hgetall(self, key: str):
        value = await self.service.hgetall(key)
        return {"key": key, "fields": value}
    
    async def hdel(self, key: str, field: str):
        success = await self.service.hdel(key, field)
        if not success:
            raise HTTPException(status_code=404, detail="Field not found")
        return {"success": success, "key": key, "field": field}
    
    async def lpush(self, key: str, operation: RedisListOperation):
        length = await self.service.lpush(key, operation.value)
        return {"success": True, "key": key, "list_length": length}
    
    async def rpush(self, key: str, operation: RedisListOperation):
        length = await self.service.rpush(key, operation.value)
        return {"success": True, "key": key, "list_length": length}
    
    async def lrange(self, key: str, start: int = 0, end: int = -1):
        values = await self.service.lrange(key, start, end)
        return {"key": key, "values": values, "count": len(values)}
    
    async def lset(self, key: str, index: int, operation: RedisListOperation):
        success = await self.service.lset(key, index, operation.value)
        return {"success": success, "key": key, "index": index}
    
    async def lrem(self, key: str, value: str, count: int = 0):
        removed = await self.service.lrem(key, value, count)
        return {"success": True, "key": key, "removed_count": removed}
    
    async def increment(self, key: str, operation: RedisIncrementOperation):
        new_value = await self.service.increment(key, operation.amount)
        return {"key": key, "new_value": new_value}
    
    async def delete_key(self, key: str):
        success = await self.service.delete_key(key)
        if not success:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"success": success, "key": key}
    
    async def expire(self, key: str, operation: RedisExpireOperation):
        success = await self.service.expire(key, operation.seconds)
        return {"success": success, "key": key, "seconds": operation.seconds}
    
    async def ttl(self, key: str):
        ttl = await self.service.ttl(key)
        return {"key": key, "ttl": ttl}