from worker import Worker
import json
import asyncio
from connections import init_pool, open_pg_pool_connection, close_pg_pool_connection
from repository import MessageRepository
from models import Answer
from repository_redis import TaskConsumerRepo

async def task_consumer():
    redis_repo = TaskConsumerRepo()
    message_repo = MessageRepository()

    while True:
        try:
            result = await redis_repo.pop_task()
            if result is None:
                continue
            _, payload = result
            task = json.loads(payload)
            user_id = task['user_id']
            data = task['message']
            message = Worker.execute(data)
            await message_repo.put_message(Answer(user_id=user_id, message=message))

        except Exception as e:
            print("Worker error:", e)
            await asyncio.sleep(1)


async def main():
    print('Worker started')

    init_pool()
    await open_pg_pool_connection()

    try:
        await task_consumer()

    except KeyboardInterrupt:
        print('Stopping worker')

    finally:
        print('Closing connection')
        await close_pg_pool_connection()


if __name__ == '__main__':
    asyncio.run(main())