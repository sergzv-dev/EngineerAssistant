from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Router

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Hello! Bot started")