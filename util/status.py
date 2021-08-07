from rq import Worker

from datetime import datetime
import humanize


import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import config

def format_time(time):
    if time:
        return time.strftime('%m/%d/%Y %I:%M:%S %p %Z')
    else:
        return "---"

def worker_name(worker):
    return worker.name

# Returns all workers registered in this connection
workers = Worker.all(connection=config.redis)
workers.sort(key=worker_name)

for worker in workers:
    print("Worker:", worker.name)
    print(" -state:", worker.state)
    print(" -birth:", format_time(worker.birth_date))
    
    current_job = worker.get_current_job()
    if current_job:
        print(" -current job: {name} - started: {start} ({elapsed})".format(
            name= current_job.func_name, 
            start= format_time(current_job.started_at),
            elapsed= humanize.naturaltime(datetime.utcnow() - current_job.started_at)))
    else:
        print("-current job:  No job running")
       