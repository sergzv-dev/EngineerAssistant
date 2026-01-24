from connections import get_pg_connection

def create_tables() -> None:
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)

def drop_tables() -> None:
    with get_pg_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DROP TABLE users')

create_tables()