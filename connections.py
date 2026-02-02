import os
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

load_dotenv()

DSN = (
    f"host={os.getenv('POSTGRES_HOST')} "
    f"port={os.getenv('POSTGRES_PORT')} "
    f"dbname={os.getenv('POSTGRES_DB')} "
    f"user={os.getenv('POSTGRES_USER')} "
    f"password={os.getenv('POSTGRES_PASSWORD')}"
    )

class PGConnectionPool():
    def __init__(self):
        self.pool = (AsyncConnectionPool
            (
            conninfo = DSN,
            min_size = 1,
            max_size = 5,
            open = False
            )
        )

    async def open_connection(self):
        await self.pool.open()

    async def close_connection(self):
        await self.pool.close()

    def get_conn(self):
        return self.pool.connection()


def get_redis_connection():
    return Redis(host=os.getenv('REDIS_HOST'),
                 port=int(os.getenv('REDIS_PORT')),
                 decode_responses=True,
                 socket_timeout=5,
                 socket_connect_timeout=2)