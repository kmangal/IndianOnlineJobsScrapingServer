from redis import Redis
from rq import Connection, Queue, Worker

from config import REDIS_ENDPOINT

import util.scrapelogger as scrapelogger


redis = Redis(host=REDIS_ENDPOINT, port=6379, username='default')
queue = Queue(connection=redis)

logger = scrapelogger.ScrapeLogger('error-log', 'errors.log')

def write_error_log(job, exc_type, exc_value, traceback):
    logger.log.error(
        "Uncaught exception for {func}({args})".format(func = job.func_name, args = str(job.kwargs)),
        exc_info=(exc_type, exc_value, exc_traceback))


# Start a worker
with Connection(connection=redis):
    worker = Worker([queue], connection=redis, name='worker1', exception_handlers=[write_error_log])
    worker.work()
