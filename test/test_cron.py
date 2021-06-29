from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from datetime import datetime

import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import config
import tasks as test_tasks


q = Queue(connection = config.redis)
scheduler = Scheduler(connection= config.redis)

def test():
    
    scheduler.cron(
        '* * * * *',                                        # A cron string (e.g. "0 0 * * 0")
        func= test_tasks.test_print,                  # Function to be queued
        kwargs={},                               # Keyword arguments passed into function when executed
        repeat= 10,                                         # Repeat this number of times (None means repeat forever)
        queue_name= 'default',                                # In which queue the job should be put in
        meta={'type': 'test'},                                  # Arbitrary pickleable data on the job itself
        use_local_timezone= True                              # Interpret hours in the local timezone
    )
    
if __name__ == '__main__':
    test()
    
