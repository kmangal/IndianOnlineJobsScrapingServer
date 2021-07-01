import sys
import os
from rq.command import send_stop_job_command

from rq.worker import Worker

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

import config


if __name__ == '__main__':
    worker = Worker.find_by_key('rq:worker:{}'.format(sys.argv[1]))

    # This will raise an exception if job is invalid or not currently executing
    send_stop_job_command(config.redis, worker.get_current_job().get_id())