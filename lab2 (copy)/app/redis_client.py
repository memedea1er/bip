import redis.asyncio as redis
from typing import Optional

class RedisClient:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
    
    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except:
            return False
    
    async def close(self):
        await self.client.close()