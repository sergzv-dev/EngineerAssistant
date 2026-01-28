from models import UserInDB, UserLoginInDB, MessageModel, Answer, Question, MessageGet, MessagesOut
from connections import get_pg_connection

class Repository:
    @classmethod
    def get_conn(cls):
        return get_pg_connection()

class UserRepository(Repository):
    def add_user(self, user: UserInDB) -> None:
        with self.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO users (username, email, hashed_password)
                                VALUES (%(username)s, %(email)s, %(hashed_password)s)''',
                               user.model_dump(include={'username', 'email', 'hashed_password'}))

    def get_user_auth_data(self, username) -> UserLoginInDB|None:
        with self.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, hashed_password FROM users WHERE username = %(username)s',
                               {'username': username})
                row = cursor.fetchone()
                if not row:
                    return None
                return UserLoginInDB(id=row[0], hashed_password=row[1])

#test methods
    def get_all_users(self):
        with self.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users')
                rows = cursor.fetchall()
                return rows


class MessageRepository(Repository):
    def put_message(self, message: Question|Answer):
        with self.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO messages (user_id, message, message_type) VALUES (%(user_id)s, %(message)s, %(message_type)s)',
                               message.model_dump(include={'user_id', 'message', 'message_type'}))

    def get_messages(self, req: MessageGet) -> MessagesOut:
        with self.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''SELECT * FROM messages WHERE user_id = %(user_id)s
                                  ORDER BY id DESC LIMIT %(limit)s OFFSET %(offset)s''',
                               req.model_dump())
                rows = cursor.fetchall()
                data = [MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4]) for row in rows]
                cursor.execute('SELECT COUNT(*) FROM messages WHERE user_id = %(user_id)', {'user_id': req.user_id})
                total = cursor.fetchone()[0]
                return MessagesOut(limit = req.limit, offset = req.offset, total = total, data=data)

    def get_last_question(self, user_id: int) -> MessageModel:
        with self.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''SELECT * FROM messages WHERE user_id = %(user_id)s AND message_type = 'Q' ORDER BY id DESC LIMIT 1''',
                               {'user_id': user_id})
                row = cursor.fetchone()
                return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])

    def get_last_answer(self, user_id: int) -> MessageModel:
        with self.get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''SELECT * FROM messages WHERE user_id = %(user_id)s AND message_type = 'A' ORDER BY id DESC LIMIT 1''',
                               {'user_id': user_id})
                row = cursor.fetchone()
                return MessageModel(id=row[0], user_id=row[1], message=row[2], message_type=row[3], created_at=row[4])