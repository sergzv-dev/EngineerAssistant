from connections import PGConnectionPool

async def create_tables() -> None:
    connection = PGConnectionPool()
    await connection.open_connection()

    async with connection.get_conn() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users
                (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)

            await cursor.execute("""
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

            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id_created ON messages (user_id, created_at DESC);")

    await connection.close_connection()


async def drop_tables() -> None:
    connection = PGConnectionPool()
    await connection.open_connection()

    async with connection.get_conn() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DROP TABLE users")
            await cursor.execute("DROP TABLE messages")

    await connection.close_connection()

create_tables()