from aiogram.filters import BaseFilter
from aiogram.types import Message
from redis_tg_repository import TGUserModeManager

user_mode_manager = TGUserModeManager()

class ExecuteModeFilter(BaseFilter):
    async def __call__(self, message: Message, mode: str) -> bool:
        return mode == "execute"


