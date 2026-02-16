from custom_exceptions import BrokerUnavailable
from models import Question
from redis.exceptions import RedisError
import asyncio
from repository_redis import TaskBrokerRepo


class TaskBroker:
    def __init__(self):
        self.repo = TaskBrokerRepo()

    async def add_task(self, question: Question) -> int:
        if await self.repo.len_queue() > 50: raise BrokerUnavailable('Queue limit exceeded')

        payload = question.model_dump_json()

        for attempt in range(3):
            try:
                await self.repo.put_new_task(payload)
                break
            except RedisError:
                if attempt == 2:
                    raise BrokerUnavailable('Redis connection error')
                await asyncio.sleep(0.3)
        return question.id