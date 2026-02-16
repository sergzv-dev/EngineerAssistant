from connections import get_redis_connection
from models import TGUserMode

class RedisRepository:
    def __init__(self):
        self.redis_client = get_redis_connection()


class TaskBrokerRepo(RedisRepository):
    async def len_queue(self):
        return await self.redis_client.llen('active_tasks')

    async def put_new_task(self, payload):
        await self.redis_client.lpush('active_tasks', payload)


class TaskConsumerRepo(RedisRepository):
    async def pop_task(self):
        return await self.redis_client.brpop('active_tasks', timeout=10)


class TGUserModeManager(RedisRepository):
    async def change_user_status(self, user_mode: TGUserMode):
        await self.redis_client.hset("tg:user:mode", user_mode.user_id, user_mode.mode)

    async def get_user_status(self, user_id: int):
        return await self.redis_client.hget("tg:user:mode", user_id)