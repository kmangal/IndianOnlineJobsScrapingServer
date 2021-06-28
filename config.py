import os
from redis import Redis

REDIS_ENDPOINT = 'task-queue.3g7al0.0001.aps1.cache.amazonaws.com'

# Only works on the server - Amazon restriction on connecting to elasticache
redis = Redis(host=REDIS_ENDPOINT, port=6379, username='default')
