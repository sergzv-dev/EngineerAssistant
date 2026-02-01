import os
from dotenv import load_dotenv
import psycopg
from redis.asyncio import Redis

load_dotenv()

def get_pg_connection():
    return psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def get_redis_connection():
    return Redis(host=os.getenv('REDIS_HOST'),
                 port=int(os.getenv('REDIS_PORT')),
                 decode_responses=True,
                 socket_timeout=5,
                 socket_connect_timeout=2)