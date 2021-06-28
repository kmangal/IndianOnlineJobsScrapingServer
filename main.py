from redis import Redis
from rq import Queue

import waahjobs.apiscraper
from tasks import print_numbers

from datetime import datetime

from config import REDIS_ENDPOINT

q = Queue(connection=Redis(host=REDIS_ENDPOINT, port=6379, username='default'))

def test():
    result = q.enqueue(print_numbers, 10)
    print(result)


def main():
    
    result = q.enqueue(
            waahjobs.apiscraper.run_scrape, 
            filedate = datetime.today().strftime('%Y%m%d_%H%M%S'),
            test = True)

    print(result)
    
if __name__ == '__main__':
    main()
    
