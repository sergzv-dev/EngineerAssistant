import asyncio
from models import UserInDB, UserLoginInDB, MessageModel, Answer, Question, MessageGet, MessagesOut, TGGetAnswer
from psycopg_pool import AsyncConnectionPool

class AsyncPGRepository:
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool

    async def _execute(self, sql: str, args_dict: dict|None = None, *, fetch_all = False):
        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, args_dict)
                if fetch_all:
                    return await cursor.fetchall()
                else:
                    return await cursor.fetchone()


class UserRepository(AsyncPGRepository):
    async def add_user(self, user: UserInDB) -> int:
        sql = '''INSERT INTO users (username, email, hashed_password)
        VALUES (%(username)s, %(email)s, %(hashed_password)s)
        RETURNING id'''
        args_dict = user.model_dump(include={'username', 'email', 'hashed_password'})

        row = await self._execute(sql, args_dict)
        user_id = int(row[0])
        return user_id

    async def get_user_auth_data(self, username) -> UserLoginInDB|None:
        sql = 'SELECT id, hashed_password FROM users WHERE username = %(username)s'
        args_dict = {'username': username}
        row = await self._execute(sql, args_dict)
        if not row:
            return None
        return UserLoginInDB(id=row[0], hashed_password=row[1])

#test methods
    async def get_all_users(self):
        sql = 'SELECT * FROM users'
        rows = await self._execute(sql, fetch_all = True)
        return rows


class MessageRepository(AsyncPGRepository):
    async def put_message(self, message: Question|Answer) -> int:
        sql = '''INSERT INTO messages (user_id, message, message_type)
        VALUES (%(user_id)s, %(message)s, %(message_type)s)
        RETURNING id'''
        args_dict = message.model_dump(include={'user_id', 'message', 'message_type'})
        row = await self._execute(sql, args_dict)
        message_id = int(row[0])
        return message_id

    async def get_messages(self, req: MessageGet) -> MessagesOut:
        sql_messages = '''SELECT * FROM messages WHERE user_id = %(user_id)s
        ORDER BY id DESC LIMIT %(limit)s OFFSET %(offset)s'''
        args_dict_messages = req.model_dump()
        sql_count = 'SELECT COUNT(*) FROM messages WHERE user_id = %(user_id)s'
        args_dict_count = {'user_id': req.user_id}

        messages_rows, count_row = await asyncio.gather(
            self._execute(sql_messages, args_dict_messages, fetch_all = True),
            self._execute(sql_count, args_dict_count)
        )

        data = [MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4]) for row
                in messages_rows]
        total = count_row[0]
        return MessagesOut(limit=req.limit, offset=req.offset, total=total, data=data)

    async def get_last_question(self, user_id: int) -> MessageModel:
        sql = '''SELECT * FROM messages WHERE user_id = %(user_id)s AND message_type = 'Q' ORDER BY id DESC LIMIT 1'''
        args_dict = {'user_id': user_id}
        row = await self._execute(sql, args_dict)
        return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])

    async def get_last_answer(self, user_id: int) -> MessageModel:
        sql = '''SELECT * FROM messages WHERE user_id = %(user_id)s AND message_type = 'A' ORDER BY id DESC LIMIT 1'''
        args_dict = {'user_id': user_id}
        row = await self._execute(sql, args_dict)
        return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])


class TelegramRepository(AsyncPGRepository):
    async def register_tg_user(self,user_id: int, telegram_id: int):
        sql = '''UPDATE users SET telegram_id = %(telegram_id)s WHERE id = %(user_id)s'''
        args_dict = {'user_id': user_id, 'telegram_id': telegram_id}
        row = await self._execute(sql, args_dict)

    async def get_user_id_by_tg(self, telegram_id: int) -> int|None:
        sql = 'SELECT id FROM users WHERE telegram_id = %(telegram_id)s'
        args_dict = {'telegram_id': telegram_id}
        row = await self._execute(sql, args_dict)
        if not row:
            return None
        return int(row[0])

    async def get_answer_for_tg(self, answer_data: TGGetAnswer) -> MessageModel|None:
        sql = '''SELECT * FROM messages
        WHERE user_id = %(user_id)s AND message_type = 'A' AND id > %(last_message_id)s
        ORDER BY id DESC LIMIT 1'''
        args_dict = answer_data.model_dump()
        row = await self._execute(sql, args_dict)
        if not row:
            return None
        return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])