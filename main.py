from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler


import waahjobs.apiscraper
from tasks import print_numbers

from datetime import datetime

import config

q = Queue(connection = config.redis)
scheduler = Scheduler(connection= config.redis)


def test():
    result = q.enqueue(print_numbers, 10)
    print(result)


def main():
    
    scheduler.cron(
        '30 18 * * *',                                        # A cron string (e.g. "0 0 * * 0")
        func= waahjobs.apiscraper.run_scrape,                  # Function to be queued
        kwargs={'test': False},                               # Keyword arguments passed into function when executed
        repeat= None,                                         # Repeat this number of times (None means repeat forever)
        queue_name= 'default',                                # In which queue the job should be put in
        meta={'site': 'waahjobs'},                                  # Arbitrary pickleable data on the job itself
        use_local_timezone= True                              # Interpret hours in the local timezone
    )
    
if __name__ == '__main__':
    main()
    
