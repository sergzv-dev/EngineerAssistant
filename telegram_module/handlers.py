from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import Router, BaseMiddleware
from models import TGUserMode, Question, TGGetAnswer
from repository_redis import TGUserModeManager
from repository import TelegramRepository, MessageRepository
from task_broker import TaskBroker
from custom_exceptions import BrokerUnavailable
import asyncio
from custom_filters import ExecuteModeFilter

router = Router()
authorized_router = Router()
fallback_router = Router()

user_mode_manager = TGUserModeManager()
db_tg_repository = TelegramRepository()
db_message_repo = MessageRepository()
db_t_broker = TaskBroker()

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        db_user_id = await db_tg_repository.get_user_id_by_tg(int(event.from_user.id))
        if not db_user_id:
            await event.answer("register your tg id")
            return None
        data["db_user_id"] = db_user_id
        mode = await user_mode_manager.get_user_status(int(event.from_user.id))
        data["mode"] = mode
        return await handler(event, data)

authorized_router.message.outer_middleware(AuthMiddleware())

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

@router.message(Command("stop"))
async def stop(message: Message):
    user_mode = TGUserMode(user_id=message.from_user.id, mode="main")
    await user_mode_manager.change_user_status(user_mode)
    await message.answer("main menu")

@router.message(Command("get_user_id"))
async def get_user_id(message: Message):
    await message.answer(str(message.from_user.id))

@authorized_router.message(Command("execute"))
async def execute_mode(message: Message):
    user_mode = TGUserMode(user_id=message.from_user.id, mode="execute")
    await user_mode_manager.change_user_status(user_mode)
    await message.answer("enter the number")

@authorized_router.message(ExecuteModeFilter(), lambda message: message.text and not message.text.startswith("/"))
async def execute(message: Message, db_user_id: int):
    if not message.text.isdigit():
        await message.answer("enter number")
        return

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
            return
        await asyncio.sleep(delay)

    await message.answer("The server is unavailable, please try again later")

@fallback_router.message()
async def fallback(message: Message):
    await message.answer("Unknown command")
    return