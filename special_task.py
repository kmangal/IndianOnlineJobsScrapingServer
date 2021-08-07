import sys
import os

from rq import Queue

import tasks

import config

def redo_shine_details(infile, outfile, logfile):
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.shine_detail_scrape, 
       kwargs = {'infile' : infile,
        'outfile' : outfile,
        'log' : logfile},
        job_timeout = 60 * 60 * 24 * 7)
        
def redo_timesjobs_details():
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.timesjobs_detail_scrape, 
        job_timeout = 60 * 60 * 24 * 7)


def redo_monster_details():
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.monster_detail_scrape,
        job_timeout = 60 * 60 * 24 * 7)    

def redo_teamlease_details():
    q = Queue(connection = config.redis)
    result = q.enqueue(tasks.teamlease_detail_scrape,
        job_timeout = 60 * 60 * 24 * 7)    


if __name__ == '__main__':
    #redo_timesjobs_details(
    #    infile= os.path.expanduser('~/jobs_scraping/timesjobs/output/mainpage/timesjobs_mainpage_20210630_032644.csv'),
    #    outfile = os.path.expanduser('~/jobs_scraping/timesjobs/output/details/timesjobs_details_20210630_032644.csv'),
    #    logfile= os.path.expanduser('~/jobs_scraping/timesjobs/log/20210630_032644.log')
    #    )

    #redo_shine_details(
    #    infile= 'shine_mainpage_20210707_134204.csv',
    #    outfile = 'shine_details_20210707_134204.csv',
    #    logfile= '20210707_134204_v2.log'
    #    )

    if sys.argv[1] == 'teamlease-details':
        redo_teamlease_details()
    elif sys.argv[1] == 'monster-details':
        redo_monster_details()
    elif sys.argv[1] == 'timesjobs-details':
        redo_timesjobs_details()