import asyncio
import os
from dotenv import load_dotenv

from aiogram import Dispatcher, Bot
from routers import router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def t_main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(t_main())
