import sys

from rq_scheduler import Scheduler

from datetime import datetime

import tasks

import config


TASK_DICT = {}
TASK_DICT['waahjobs'] = tasks.waahjobs_scrape
TASK_DICT['monster'] = tasks.monster_scrape
TASK_DICT['timesjobs'] = tasks.timesjobs_scrape
TASK_DICT['teamlease'] = tasks.teamlease_scrape
TASK_DICT['shine'] = tasks.shine_scrape


def reschedule(scheduler, job, site):
    
    scheduler.cancel(job)
    
    if site == 'waahjobs':
        dayskip = 1
        scheduler.schedule(
            scheduled_time=  datetime.utcnow(),                            # Time for first execution, in UTC timezone
            func= TASK_DICT[site],                  # Function to be queued
            kwargs={'test': False},                               # Keyword arguments passed into function when executed
            interval = 60 * 60 * 24 * dayskip,                               # Interval in seconds
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta= {'site': site, 'type' : 'scrape', 'name' : site},                                  # Arbitrary pickleable data on the job itself
            timeout = 60 * 60 * 24 * dayskip
        )
    else:
        dayskip = 7
    
        scheduler.schedule(
            scheduled_time=  datetime.utcnow(),                            # Time for first execution, in UTC timezone
            func= TASK_DICT[site],                  # Function to be queued
            interval = 60 * 60 * 24 * dayskip,                               # Interval in seconds
            repeat= None,                                         # Repeat this number of times (None means repeat forever)
            queue_name= 'default',                                # In which queue the job should be put in
            meta= {'site': site, 'type' : 'scrape', 'name' : site},                                  # Arbitrary pickleable data on the job itself
            timeout = 60 * 60 * 24 * dayskip
        )

   
    
if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        raise Exception("Need to list at least one site")
    
    scheduler = Scheduler(connection= config.redis)

    scheduled_jobs = {}
    for job in scheduler.get_jobs():
        scheduled_jobs[job.meta['site']] = job


    for site in sys.argv[1:]:
        if site in scheduled_jobs:
            reschedule(scheduler, scheduled_jobs[site], site)
        else:
            print("{s} is not currently scheduled".format(s = site))

        
    
