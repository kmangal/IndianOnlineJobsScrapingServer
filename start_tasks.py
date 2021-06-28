from redis import Redis
from rq import Queue

import waahjobs

REDIS_ENDPOINT = 'task-queue.3g7al0.0001.aps1.cache.amazonaws.com'

q = Queue(connection=Redis(host=ENDPOINT, port=6379, username='default'))
result = q.enqueue(waahjobs.waahjobs_scrape.run_scrape)
