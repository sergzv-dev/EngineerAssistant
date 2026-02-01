from worker import Worker
import json
import asyncio
from connections import get_redis_connection
from repository import MessageRepository
from models import Answer

message_repo = MessageRepository()


async def task_consumer():
    print('Worker started')

    redis_client = get_redis_connection()

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
            message_repo.put_message(Answer(user_id=user_id, message=message))

        except Exception as e:
            print("Worker error:", e)
            await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(task_consumer())