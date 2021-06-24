import os
from datetime import datetime

import argparse

import sys
sys.path.append('../')
import util.export_to_dropbox

import shine_details

import util.scrapelogger as scrapelogger

def run_full_scrape(filedate):

    mainpage_local = 'output/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'output/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    details_local = 'output/details/shine_details_{fd}.csv'.format(fd=filedate)
    logfile_local = 'log/{fd}.log'.format(fd=filedate) # reuse the same logfile

    os.system('scrapy crawl Shine -o "{mpl}" -a jobcountfile="{jcl}" -a logfile="{lfl}"'.format(
        mpl = mainpage_local, 
        jcl = jobcount_local, 
        lfl = logfile_local))

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    details_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/details/shine_details_{fd}.csv'.format(fd=filedate)
    logfile_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/log/{fd}.log'.format(fd=filedate)
    
    util.export_to_dropbox.move_to_dropbox(mainpage_local, mainpage_dropbox)
    util.export_to_dropbox.move_to_dropbox(jobcount_local, jobcount_dropbox)
    
    # Run detail scrape
    shine_details.run_scrape(
        inputfile = mainpage_local, 
        outputfile = details_local,
        logfile = logfile_local)
        
    # Move the log and details files
    util.export_to_dropbox.move_to_dropbox(details_local, details_dropbox)
    util.export_to_dropbox.move_to_dropbox(logfile_local, logfile_dropbox)


def test_scrape(filedate):
    raise Exception

    mainpage_local = 'test/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'test/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'test/log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Shine -o "{mainpage_local}" -a test=True -a jobcountfile="{jobcount_local}" -a logfile="{logfile_local}"'.format(mainpage_local = mainpage_local, jobcount_local = jobcount_local, logfile_local = logfile_local))
    

def start_logging(filepath):
    logger = scrapelogger.ScrapeLogger('shine-scraper', logfile)
    sys.excepthook = logger.exceptionhandler
    return logger

if __name__ == '__main__':

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action='store_true', help = "Run full scrape")
    args = parser.parse_args()

    # Default behavior is to run a test
    if args.full:
        logfile = 'log/{fd}.log'.format(fd=filedate)
        logger = start_logging(logfile)
        run_full_scrape(filedate)    
    else:
        logfile = 'test/log/{fd}.log'.format(fd=filedate)
        logger = start_logging(logfile)
        test_scrape(filedate)
    