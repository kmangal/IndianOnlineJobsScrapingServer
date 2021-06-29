from rq_scheduler import Scheduler
from datetime import timedelta

import sys
sys.path.append('../')
import config

scheduler = Scheduler(connection= config.redis)

# get all jobs for the 24 hour
job_instances = scheduler.get_jobs(with_times = True, until=timedelta(hours=24))

for job, time in job_instances:
    print(job.func_name, time)
    
