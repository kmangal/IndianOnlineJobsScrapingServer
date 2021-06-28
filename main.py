from redis import Redis
from rq import Queue

import waahjobs
from tasks import print_numbers

REDIS_ENDPOINT = 'task-queue.3g7al0.0001.aps1.cache.amazonaws.com'

q = Queue(connection=Redis(host=REDIS_ENDPOINT, port=6379, username='default'))

def test():
    result = q.enqueue(print_numbers, 10)
    print(result)


def main():
    result = q.enqueue(waahjobs.waahjobs_scrape.run_scrape)
    print(result)
    
if __name__ == '__main__':
    test()
    
