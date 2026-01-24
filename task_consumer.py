from worker import Worker
import json
from multiprocessing import Pool
from connections import get_redis_connection

def task_consumer(task):
    task_id = task['task_id']
    data = task['data']

    w_redis_client = get_redis_connection()
    res = Worker.execute(data)
    w_redis_client.hset('done_tasks', task_id, res)


if __name__ == '__main__':
    redis_client = get_redis_connection()

    with Pool(processes=4) as pool:

        while True:
            _, payload = redis_client.brpop('active_tasks')
            task = json.loads(payload)
            pool.apply_async(task_consumer, args=(task,))