import os
from datetime import datetime

import argparse

import sys
sys.path.append('../')
import util

def run_full_scrape(filedate):
    mainpage_local = 'output/mainpage/teamlease_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'output/jobcount/teamlease_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Teamlease -o "{mpl}" -a jobcountfile="{jcl}" -a logfile="{lfl}"'.format(
        mpl = mainpage_local, 
        jcl = jobcount_local, 
        lfl = logfile_local))

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/mainpage/teamlease_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/jobcount/teamlease_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/log/{fd}.log'.format(fd=filedate)
    
    util.export_to_dropbox.move_to_dropbox(mainpage_local, mainpage_dropbox)
    util.export_to_dropbox.move_to_dropbox(jobcount_local, jobcount_dropbox)
    util.export_to_dropbox.move_to_dropbox(logfile_local, logfile_dropbox)


def test_scrape(filedate):
    mainpage_local = 'test/mainpage/teamlease_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'test/jobcount/teamlease_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'test/log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Teamlease -o "{mainpage_local}" -a test=True -a jobcountfile="{jobcount_local}" -a logfile="{logfile_local}"'.format(mainpage_local = mainpage_local, jobcount_local = jobcount_local, logfile_local = logfile_local))
    

######## Main #############

filedate = datetime.today().strftime('%Y%m%d')

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("--full", help = "Run full scrape")
args = parser.parse_args()

# Default behavior is to run a test
if args.full:
    run_full_scrape(filedate)    
else:
    test_scrape(filedate)
    