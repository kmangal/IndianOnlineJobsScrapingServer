from rq import Worker

from datetime import datetime
import humanize

import config

# Returns all workers registered in this connection
workers = Worker.all(connection=config.redis)

for worker in workers:
    print("Worker:", worker.name)
    print(" -state:", worker.state)
    print(" -birth:", worker.birth_date)
    
    current_job = worker.get_current_job()
    
    print(" -current job: {name} - started: {start} ({elapsed})".format(
        name= current_job.func_name, 
        start= current_job.started_at,
        elapsed= humanize.naturaltime(datetime.utcnow() - current_job.started_at)))