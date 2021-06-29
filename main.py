from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from datetime import datetime

import tasks

import config


def test_connection():
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.test_print, 'hi')
    print(result)


def main():

    scheduler = Scheduler(connection= config.redis)
    
    scheduled_jobs = [job.meta['site'] for job in scheduler.get_jobs()]
            
    if 'waahjobs' not in scheduled_jobs:
        scheduler.cron(
            '30 18 * * *',                                        # A cron string (e.g. "0 0 * * 0")
            func= tasks.waahjobs_scrape,                  # Function to be queued
            kwargs={'test': False},                               # Keyword arguments passed into function when executed
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'waahjobs'},                                  # Arbitrary pickleable data on the job itself
            use_local_timezone= True                              # Interpret hours in the local timezone
        )

    
    if 'monster' not in scheduled_jobs:
        scheduler.cron(
            '30 18 1/4 * *',                                        # A cron string (e.g. "0 0 * * 0")
            func= tasks.monster_scrape,                  # Function to be queued
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'monster'},                                  # Arbitrary pickleable data on the job itself
            use_local_timezone= True                              # Interpret hours in the local timezone
        )
        
        
    if 'shine' not in scheduled_jobs:
        scheduler.cron(
            '30 18 2/4 * *',                                        # A cron string (e.g. "0 0 * * 0")
            func= tasks.shine_scrape,                               # Function to be queued
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'shine'},                                  # Arbitrary pickleable data on the job itself
            use_local_timezone= True                              # Interpret hours in the local timezone
        )
        
    
if __name__ == '__main__':
    main()
    
