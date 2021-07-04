from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from datetime import datetime, timedelta

import tasks

import config


def test_connection():
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.test_print, 'hi')
    print(result)


def main():

    scheduler = Scheduler(connection= config.redis)
    
    currentdate = datetime.utcnow()
    base_start_time = datetime(year = currentdate.year, month = currentdate.month, day = currentdate.day, hour = 18, minute = 30, second = 0)

    
    scheduled_jobs = [job.meta['site'] for job in scheduler.get_jobs()]
            
    if 'waahjobs' not in scheduled_jobs:
        
        scheduler.schedule(
            scheduled_time=  base_start_time,                            # Time for first execution, in UTC timezone
            func= tasks.waahjobs_scrape,                  # Function to be queued
            kwargs={'test': False},                               # Keyword arguments passed into function when executed
            interval = 60 * 60 * 24,                               # Interval in seconds
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'waahjobs'},                                  # Arbitrary pickleable data on the job itself
            timeout = 60 * 60 * 24
        )
        
    if 'monster' not in scheduled_jobs:
        
        scheduler.schedule(
            scheduled_time = base_start_time,                            # Time for first execution, in UTC timezone
            func= tasks.monster_scrape,                  # Function to be queued
            interval = 60 * 60 * 24 * 4,                               # Interval in seconds
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'monster'},                                  # Arbitrary pickleable data on the job itself
            timeout = 60 * 60 * 24 * 4
        )
        
        
    if 'shine' not in scheduled_jobs:
        # Start with one day delay
        
        scheduler.schedule(
            scheduled_time = base_start_time +  timedelta(days=1),        # Time for first execution, in UTC timezone
            func= tasks.shine_scrape,                                       # Function to be queued
            interval = 60 * 60 * 24 * 4,                               # Interval in seconds
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'shine'},                                  # Arbitrary pickleable data on the job itself
            timeout = 60 * 60 * 24 * 4
        )

    if 'teamlease' not in scheduled_jobs:
        # Start with two day delay
        
        scheduler.schedule(
            scheduled_time = base_start_time +  timedelta(days=2),        # Time for first execution, in UTC timezone
            func= tasks.teamlease_scrape,                                       # Function to be queued
            interval = 60 * 60 * 24 * 4,                               # Interval in seconds
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'teamlease'},                                  # Arbitrary pickleable data on the job itself
            timeout = 60 * 60 * 24 * 4
        )

    if 'timesjobs' not in scheduled_jobs:
        # Start with three day delay
        
        scheduler.schedule(
            scheduled_time = base_start_time + timedelta(days=3),                            # Time for first execution, in UTC timezone
            func= tasks.timesjobs_scrape,                  # Function to be queued
            interval = 60 * 60 * 24 * 4,                               # Interval in seconds
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta={'site': 'timesjobs'},                                  # Arbitrary pickleable data on the job itself
            timeout = 60 * 60 * 24 * 4
        )    
    
if __name__ == '__main__':
    main()
    
