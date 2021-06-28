from rq_scheduler import Scheduler
from datetime import timedelta

import sys
sys.path.append('../')
import config

scheduler = Scheduler(connection= config.redis)

# get all jobs for the 24 hours
list_of_job_instances = scheduler.get_jobs(until=timedelta(hours=24))

for job in list_of_job_instances:
    print(job.func_name, job.get_status())