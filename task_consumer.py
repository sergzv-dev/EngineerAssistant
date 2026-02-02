from worker import Worker
import json
import asyncio
from connections import get_redis_connection
from repository import MessageRepository
from models import Answer

async def task_consumer():
    print('Worker started')

    redis_client = get_redis_connection()
    message_repo = MessageRepository()

    await message_repo.connection.open_connection()

    while True:
        try:
            result = await redis_client.brpop('active_tasks', timeout=5)
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

        except KeyboardInterrupt as e:
            message_repo.connection.close_connection()
            raise e

if __name__ == '__main__':
    asyncio.run(task_consumer())