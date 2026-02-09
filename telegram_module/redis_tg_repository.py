from connections import get_redis_connection
from models import TGUserMode

class TGRedisRepository:
    def __init__(self):
        self.redis_client = get_redis_connection()

class TGUserModeManager(TGRedisRepository):
    async def change_user_status(self, user_mode: TGUserMode):
        payload = user_mode.model_dump_json()
        await self.redis_client.hset("tg:user:mode", payload)

    async def get_user_status(self, user_id: int):
        return await self.redis_client.hget("tg:user:mode", user_id)