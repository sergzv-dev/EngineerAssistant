from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Router
from models import TGUserMode, Question, TGGetAnswer
from redis_tg_repository import TGUserModeManager
from repository import TelegramRepository, MessageRepository
from task_broker import TaskBroker
from custom_exceptions import BrokerUnavailable
import asyncio

router = Router()

user_mode_manager = TGUserModeManager()
db_tg_repository = TelegramRepository()
db_message_repo = MessageRepository()
db_t_broker = TaskBroker()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Hello! Bot started")

@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        """
        /start - starting bot \n
        /execute - turns on operating mode
        /get_user_id - get your id
        /stop - return to main menu
        """
    )

@router.message(Command("execute"))
async def execute_mode(message: Message):
    user_mode = TGUserMode(user_id=message.from_user.id, mode="execute")
    await user_mode_manager.change_user_status(user_mode)
    await message.answer("enter the number")

@router.message(Command("stop"))
async def stop(message: Message):
    user_mode = TGUserMode(user_id=message.from_user.id, mode="main")
    await user_mode_manager.change_user_status(user_mode)
    await message.answer("main menu")

@router.message(Command("get_user_id"))
async def get_user_id(message: Message):
    await message.answer(str(message.from_user.id))

@router.message(lambda message: message.text and not message.text.startswith("/"))
async def execute(message: Message):
    if await user_mode_manager.get_user_status(int(message.from_user.id)) != "execute":
        return

    if not message.text.isdigit():
        await message.answer("enter number")
        return

    db_user_id = await db_tg_repository.get_user_id_by_tg(int(message.from_user.id))

    question_data = Question(user_id=db_user_id, message=message.text)
    db_message_id = await db_message_repo.put_message(question_data)
    question_data = question_data.model_copy(update={'id': db_message_id})

    try:
        db_message_id = await db_t_broker.add_task(question_data)
    except BrokerUnavailable:
        await message.answer("The server is unavailable, please try again later")
        return

    answer_data = TGGetAnswer(user_id=db_user_id, last_message_id=db_message_id)

    await asyncio.sleep(0.5)

    for delay in range(1,5):
        tg_answer = await db_tg_repository.get_answer_for_tg(answer_data)
        if tg_answer:
            await message.answer(tg_answer.message)
        await asyncio.sleep(delay)

    await message.answer("The server is unavailable, please try again later")