# Adds special (i.e. non-routine) tasks to the task queue

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

    if sys.argv[1] == 'teamlease-details':
        redo_teamlease_details()
    elif sys.argv[1] == 'monster-details':
        redo_monster_details()
    elif sys.argv[1] == 'timesjobs-details':
        redo_timesjobs_details()