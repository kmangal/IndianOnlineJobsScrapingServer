from redis import Redis
import logging

# NOTE: This script will not work on the local machine, elasticache needs to be accessed by a computer in the same availability zone

REDIS_ENDPOINT = 'task-queue.3g7al0.0001.aps1.cache.amazonaws.com'

logging.basicConfig(level=logging.INFO)
redis = redis = Redis(host=REDIS_ENDPOINT, port=6379, username='default')

redis.ping()
print('Connected to Redis')
