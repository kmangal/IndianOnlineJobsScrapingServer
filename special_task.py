import sys
import os

from rq import Queue

from datetime import datetime, timedelta

import tasks

import config


def redo_timesjobs_details(infile, outfile, logfile):
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.teamlease_detail_scrape, 
       {'infile' : infile,
        'outfile' : outfile,
        'log' : logfile})
	
if __name__ == '__main__':
    redo_timesjobs_details(
        infile= os.path.expanduser('~/jobs_scraping/timesjobs/output/mainpage/timesjobs_mainpage_20210630_032644.csv'),
        outfile = os.path.expanduser('~/jobs_scraping/timesjobs/output/details/timesjobs_details_20210630_032644.csv'),
        logfile=os.path.expanduser('~/jobs_scraping/timesjobs/log/20210630_032644.log')
        )
        