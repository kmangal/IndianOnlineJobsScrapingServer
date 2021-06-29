from rq_scheduler import Scheduler
from datetime import timedelta

import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import config

scheduler = Scheduler(connection= config.redis)

def list_jobs(number_days = 7):
    '''get all jobs in the next timeframe - week by default'''

    job_instances = scheduler.get_jobs(with_times = True, until=timedelta(days=number_days))

    print("Jobs in next {days} days".format(days = number_days))
    for job, time in job_instances:
        print(job.func_name, time)
    

if __name__ == '__main__':
    
    if len(sys.argv) > 1 and sys.argv[1].isnumeric():
        list_jobs(int(sys.argv[1]))
    else:
        list_jobs()
