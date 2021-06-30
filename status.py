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
    print(" -current job: {name}  - started: {start} ({elapsed} elapsed)".format(
        name=worker.current_job.func_name, 
        start=worker.current_job.started_at,
        elapsed= humanize.naturaltime(datetime.utcnow() - worker.current_job.started_at)))