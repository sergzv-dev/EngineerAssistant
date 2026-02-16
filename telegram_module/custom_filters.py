from aiogram.filters import BaseFilter
from aiogram.types import Message

class ExecuteModeFilter(BaseFilter):
    async def __call__(self, message: Message, mode: str) -> bool:
        return mode == "execute"


