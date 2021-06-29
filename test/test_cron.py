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
import testtasks


q = Queue(connection = config.redis)
scheduler = Scheduler(connection= config.redis)

def test():
    
    scheduler.cron(
        '* * * * *',                                        # A cron string (e.g. "0 0 * * 0")
        func= testtasks.test_print,                  # Function to be queued
        repeat= 2,                                         # Repeat this number of times (None means repeat forever)
        queue_name= 'default',                                # In which queue the job should be put in
        meta={'type': 'test'},                                  # Arbitrary pickleable data on the job itself
        use_local_timezone= True                              # Interpret hours in the local timezone
    )
    
if __name__ == '__main__':
    test()
    
