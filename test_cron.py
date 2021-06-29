from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from datetime import datetime

#import os
#import sys
#currentdir = os.path.dirname(os.path.realpath(__file__))
#parentdir = os.path.dirname(currentdir)
#sys.path.append(parentdir)

import config

import tasks

scheduler = Scheduler(connection= config.redis)

def test():
    
    scheduler.schedule(
        scheduled_time = datetime.utcnow(),
        func= tasks.test_print,                  # Function to be queued
        args=['Testing...'],
        interval = 60,
        repeat= 2,                                         # Repeat this number of times (None means repeat forever)
        queue_name= 'default',                                # In which queue the job should be put in
        meta={'type': 'test'},                                  # Arbitrary pickleable data on the job itself
    )
    
if __name__ == '__main__':
    test()
    
