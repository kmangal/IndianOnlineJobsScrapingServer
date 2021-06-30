from redis import Redis
from rq import Connection, Queue, Worker

import config

import util.scrapelogger as scrapelogger
import util.export_to_dropbox

def write_error_log(job, exc_type, exc_value, exc_traceback):
    logger = scrapelogger.ErrorLogger('error-log', 'log/error/errors.log')
    logger.log.error(
        "Uncaught exception for {func}({args})".format(func = job.func_name, args = str(job.kwargs)),
        exc_info=(exc_type, exc_value, exc_traceback))

queue = Queue(connection = config.redis)
workercount = Worker.count(connection=config.redis)

# Start a worker
with Connection(connection = config.redis):
    worker = Worker([queue], 
                    connection = config.redis, 
                    name='worker{}'.format(workercount+1), 
                    exception_handlers=[write_error_log],
                    disable_default_exception_handler=True)
                        
    worker.work()
