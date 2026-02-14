from models import UserInDB, UserLoginInDB, MessageModel, Answer, Question, MessageGet, MessagesOut, TGGetAnswer
from connections import get_pg_pool_connection

class Repository:
    @classmethod
    def get_conn(cls):
        return get_pg_pool_connection()

class UserRepository(Repository):
    async def add_user(self, user: UserInDB) -> int:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''INSERT INTO users (username, email, hashed_password)
                                VALUES (%(username)s, %(email)s, %(hashed_password)s) RETURNING id''',
                               user.model_dump(include={'username', 'email', 'hashed_password'}))
                row = await cursor.fetchone()
                user_id = int(row[0])
                return user_id

    async def get_user_auth_data(self, username) -> UserLoginInDB|None:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT id, hashed_password FROM users WHERE username = %(username)s',
                               {'username': username})
                row = await cursor.fetchone()
                if not row:
                    return None
                return UserLoginInDB(id=row[0], hashed_password=row[1])

#test methods
    async def get_all_users(self):
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT * FROM users')
                rows = await cursor.fetchall()
                return rows


class MessageRepository(Repository):
    async def put_message(self, message: Question|Answer) -> int:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''INSERT INTO messages (user_id, message, message_type)
                                  VALUES (%(user_id)s, %(message)s, %(message_type)s) RETURNING id''',
                                message.model_dump(include={'user_id', 'message', 'message_type'}))
                row = await cursor.fetchone()
                message_id = int(row[0])
                return message_id

    async def get_messages(self, req: MessageGet) -> MessagesOut:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''SELECT * FROM messages WHERE user_id = %(user_id)s
                                  ORDER BY id DESC LIMIT %(limit)s OFFSET %(offset)s''',
                               req.model_dump())
                rows = await cursor.fetchall()
                data = [MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4]) for row in rows]
                await cursor.execute('SELECT COUNT(*) FROM messages WHERE user_id = %(user_id)s', {'user_id': req.user_id})
                row = await cursor.fetchone()
                total = row[0]
                return MessagesOut(limit = req.limit, offset = req.offset, total = total, data=data)

    async def get_last_question(self, user_id: int) -> MessageModel:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''SELECT * FROM messages WHERE user_id = %(user_id)s AND message_type = 'Q' ORDER BY id DESC LIMIT 1''',
                               {'user_id': user_id})
                row = await cursor.fetchone()
                return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])

    async def get_last_answer(self, user_id: int) -> MessageModel:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''SELECT * FROM messages WHERE user_id = %(user_id)s AND message_type = 'A' ORDER BY id DESC LIMIT 1''',
                               {'user_id': user_id})
                row = await cursor.fetchone()
                return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])


class TelegramRepository(Repository):
    async def register_tg_user(self,user_id: int, telegram_id: int):
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''UPDATE users
                                    SET telegram_id = %(telegram_id)s
                                    WHERE id = %(user_id)s''',
                                     {'user_id': user_id,'telegram_id': telegram_id}
                                     )

    async def get_user_id_by_tg(self, telegram_id: int) -> int|None:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT id FROM users WHERE telegram_id = %(telegram_id)s', {'telegram_id': telegram_id})
                row = await cursor.fetchone()
                if not row: return None
                return int(row[0])

    async def get_answer_for_tg(self, answer_data: TGGetAnswer) -> MessageModel|None:
        async with self.get_conn() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''SELECT * FROM messages
                                    WHERE user_id = %(user_id)s AND message_type = 'A' AND id > %(last_message_id)s
                                    ORDER BY id DESC LIMIT 1''',
                                     answer_data.model_dump()
                                     )
                row = await cursor.fetchone()
                if not row:
                    return None
                return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])