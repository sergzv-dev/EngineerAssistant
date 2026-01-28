from connections import get_pg_connection

def create_tables() -> None:
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users
                (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages
                (
                    id         SERIAL PRIMARY KEY,
                    user_id    INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    message    TEXT        NOT NULL,
                    message_type TEXT NOT NULL
                        CHECK(message_type in ('Q', 'A')),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id_created ON messages (user_id, created_at DESC);")

def drop_tables() -> None:
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE users")
            cursor.execute("DROP TABLE messages")

create_tables()