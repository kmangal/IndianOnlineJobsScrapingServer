from rq import Queue
from rq.job import Job

import sys
import os

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

import config

def format_time(time):
    if time:
        return time.strftime('%m/%d/%Y %I:%M:%S %p %Z')
    else:
        return "---"
    
    
def list_jobs(registry):
    jobs = Job.fetch_many(registry.get_job_ids(), connection=config.redis)

    for job in jobs:
        print("{f: <28} - started: {s}  ended: {e}".format(
                f = job.func_name,
                s = format_time(job.started_at),
                e = format_time(job.ended_at)))


if __name__ == '__main__':

    queue = Queue(connection=config.redis)

    print("Finished jobs")
    print("---------------------------------------------------")
    list_jobs(queue.finished_job_registry)

    print("")
    
    print("Failed jobs")
    print("---------------------------------------------------")
    list_jobs(queue.failed_job_registry)
