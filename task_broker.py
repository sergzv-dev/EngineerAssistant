from custom_exceptions import BrokerUnavailable
from connections import get_redis_connection
from models import Question
from redis.exceptions import RedisError
import asyncio


class TaskBroker:
    def __init__(self):
        self.redis_client = get_redis_connection()

    async def add_task(self, question: Question) -> int:
        if await self.redis_client.llen('active_tasks') > 50: raise BrokerUnavailable('Queue limit exceeded')
        payload = question.model_dump_json()
        for attempt in range(3):
            try:
                await self.redis_client.lpush('active_tasks',payload)
                break
            except RedisError:
                if attempt == 2:
                    raise BrokerUnavailable('Redis connection error')
                await asyncio.sleep(0.3)
        return question.id