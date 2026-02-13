import asyncio
import os
from dotenv import load_dotenv
from connections import init_pool, open_pg_pool_connection, close_pg_pool_connection

from aiogram import Dispatcher, Bot
from routers import router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def t_main():
    init_pool()
    await open_pg_pool_connection()
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print('Stopping tg bot')
    finally:
        await close_pg_pool_connection()

if __name__ == '__main__':
    asyncio.run(t_main())
