from rq_scheduler import Scheduler
from datetime import timedelta

import os
import sys

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

import config

scheduler = Scheduler(connection= config.redis)

# get all jobs for the 24 hours
list_of_job_instances = scheduler.get_jobs()

for job in list_of_job_instances:
	scheduler.cancel(job)
