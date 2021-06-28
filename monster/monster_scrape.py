import os
from datetime import datetime

import argparse

import sys
sys.path.append('../')
import util.export_to_dropbox

import util.scrapelogger as scrapelogger

def run_full_scrape(filedate):

    mainpage_local = 'output/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'output/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    details_local = 'output/details/monster_details_{fd}.csv'.format(fd=filedate)
    logfile_local = 'log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Monster -o "{mpl}" -a jobcountfile="{jcl}" -a logfile="{lfl}"'.format(
        mpl = mainpage_local, 
        jcl = jobcount_local, 
        lfl = logfile_local))

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    details_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/details/shine_details_{fd}.csv'.format(fd=filedate)
    logfile_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/log/{fd}.log'.format(fd=filedate)
    
    util.export_to_dropbox.move_to_dropbox(mainpage_local, mainpage_dropbox)
    util.export_to_dropbox.move_to_dropbox(jobcount_local, jobcount_dropbox)
    util.export_to_dropbox.move_to_dropbox(logfile_local, logfile_dropbox)


def test_scrape(filedate):
    raise Exception

    mainpage_local = 'test/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'test/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'test/log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Shine -o "{mainpage_local}" -a test=True -a jobcountfile="{jobcount_local}" -a logfile="{logfile_local}"'.format(mainpage_local = mainpage_local, jobcount_local = jobcount_local, logfile_local = logfile_local))
    

def start_logging(filepath):
    logger = scrapelogger.ScrapeLogger('shine-scraper', logfile)
    
    return logger

if __name__ == '__main__':

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    # Initialize parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action='store_true', help = "Run full scrape")
    args = parser.parse_args()

    def emergency_log(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        if args.full:
            logger = scrapelogger.ScrapeLogger('shine-scraper', 'log/emergency_log.log')
        else:
            logger = scrapelogger.ScrapeLogger('shine-scraper', 'test/log/emergency_log.log')
        
        logger.log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
    sys.excepthook = emergency_log

    # Default behavior is to run a test
    if args.full:
        logfile = 'log/{fd}.log'.format(fd=filedate)
        run_full_scrape(filedate)    
    else:
        logfile = 'test/log/{fd}.log'.format(fd=filedate)
        test_scrape(filedate)
    