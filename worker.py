from redis import Redis
from rq import Connection, Queue, Worker

import config

import util.scrapelogger as scrapelogger
import util.export_to_dropbox

queue = Queue(connection = config.redis)

logger = scrapelogger.ErrorLogger('error-log', 'log/error/errors.log')

def write_error_log(job, exc_type, exc_value, traceback):
    logger.log.error(
        "Uncaught exception for {func}({args})".format(func = job.func_name, args = str(job.kwargs)),
        exc_info=(exc_type, exc_value, exc_traceback))

# Start a worker
with Connection(connection = config.redis):
    worker = Worker([queue], connection = config.redis, name='worker1', exception_handlers=[write_error_log])
    worker.work()
