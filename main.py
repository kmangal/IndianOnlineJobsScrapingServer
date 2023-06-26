'''
    MAIN SCHEDULER

    This file starts the main task queue and schedules recurring scrapes
    for the following sites:
        - WaahJobs
        - Shine
        - TeamLease
        - TimesJobs
        - Monster (Experimental)

    Every 4 days, run a cleaning utility to delete excess files from the server
    to avoid overusing storage space.

'''

from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from datetime import datetime, timedelta

import tasks

import config

TASKLIST = ['waahjobs', 'shine', 'teamlease', 'teamlease', 'timesjobs', 'monster', 'clean']

SCHEDULE_PARAMS = {
    'waahjobs': {
        'scheduled_time_offset': 0,
        'func' : tasks.waahjobs_scrape,
        'kwargs' : {'test': False},
        'interval' : 60 * 60 * 24,
        'meta' : {'site': 'shine', 'type' : 'scrape', 'name' : 'shine'},
        'timeout' : 60 * 60 * 24
    },
    'shine': {
        'scheduled_time_offset': 0,
        'func' : tasks.shine_scrape,
        'interval' : 60 * 60 * 24 * 6,
        'meta' : {'site': 'shine', 'type' : 'scrape', 'name' : 'shine'},
        'timeout' : 60 * 60 * 24 * 7
    },
    'teamlease': {
        'scheduled_time_offset': timedelta(days=1),
        'func' : tasks.teamlease_scrape,
        'interval' : 60 * 60 * 24 * 6,
        'meta' : {'site': 'teamlease', 'type' : 'scrape', 'name' : 'teamlease'},
        'timeout' : 60 * 60 * 24 * 7
    },
    'timesjobs': {
        'scheduled_time_offset': timedelta(days=2),
        'func' : tasks.timesjobs_scrape,
        'interval' : 60 * 60 * 24 * 6,
        'meta' : {'site': 'timesjobs', 'type' : 'scrape', 'name' : 'timesjobs'},
        'timeout' : 60 * 60 * 24 * 7
    },
    'monster': {
        'scheduled_time_offset': timedelta(days=3),
        'func' : tasks.monster_scrape,
        'interval' : 60 * 60 * 24 * 6,
        'meta' : {'site': 'monster', 'type' : 'scrape', 'name' : 'monster'},
        'timeout' : 60 * 60 * 24 * 7
    },
    'clean': {
        'scheduled_time_offset': timedelta(hours=12),
        'func' : tasks.clean,
        'interval' : 60 * 60 * 24 * 4,
        'meta' : {'site': None, 'type' : 'utility', 'name' : 'clean'},
        'timeout' : 60 * 60
    },
}


def test_connection():
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.test_print, 'hi')
    print(result)

def main():

    scheduler = Scheduler(connection= config.redis)
    
    currentdate = datetime.utcnow()
    base_start_time = datetime(year = currentdate.year, month = currentdate.month, day = currentdate.day, hour = 18, minute = 30, second = 0)

    scheduled_jobs = [job.meta['name'] for job in scheduler.get_jobs()]
    
    for task in TASKLIST:
        if task not in scheduled_jobs:

            TASK_PARAMS = SCHEDULE_PARAMS[task]

            scheduler.schedule(
                scheduled_time=  base_start_time + 
                    TASK_PARAMS['scheduled_time_offset'],           # Time for first execution, in UTC timezone
                func= TASK_PARAMS['func'],                          # Function to be queued
                kwargs=TASK_PARAMS.get('kwargs', {}),               # Keyword arguments passed into function when executed
                interval = TASK_PARAMS['interval'],                 # Interval in seconds
                repeat= None,                                       # Repeat this number of times (None means repeat forever)
                queue_name= 'default',                              # In which queue the job should be put in
                meta=TASK_PARAMS['meta'],         
                timeout = TASK_PARAMS['timeout']
            )
    
if __name__ == '__main__':
    main()
    
