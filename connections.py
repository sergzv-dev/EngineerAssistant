import os
from dotenv import load_dotenv
import psycopg
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

load_dotenv()

#postgres
def get_pg_connection():
    return psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

#postgres_pool
DSN = (
    f"host={os.getenv('POSTGRES_HOST')} "
    f"port={os.getenv('POSTGRES_PORT')} "
    f"dbname={os.getenv('POSTGRES_DB')} "
    f"user={os.getenv('POSTGRES_USER')} "
    f"password={os.getenv('POSTGRES_PASSWORD')}"
    )

pool: AsyncConnectionPool|None = None

def init_pool():
    global pool
    if pool is None:
        pool = AsyncConnectionPool(
            conninfo=DSN,
            min_size=1,
            max_size=5,
            open=False
            )

async def open_pg_pool_connection():
    if pool is None:
        raise RuntimeError("PostgreSQL pool is not initialized")
    await pool.open()

async def close_pg_pool_connection():
    if pool is None:
        raise RuntimeError("PostgreSQL pool is not initialized")
    await pool.close()

def get_pg_pool_connection():
    if pool is None:
        raise RuntimeError("PostgreSQL pool is not initialized")
    return pool.connection()


#redis
def get_redis_connection():
    return Redis(host=os.getenv('REDIS_HOST'),
                 port=int(os.getenv('REDIS_PORT')),
                 decode_responses=True,
                 socket_timeout=5,
                 socket_connect_timeout=2)