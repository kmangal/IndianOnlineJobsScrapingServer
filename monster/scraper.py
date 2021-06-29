import os
import sys

from datetime import datetime

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

import util.export_to_dropbox
import util.scrapelogger as scrapelogger

def run_full_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'output/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'output/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Monster -o "{mpl}" -a jobcountfile="{jcl}" -a logfile="{lfl}"'.format(
        mpl = mainpage_local, 
        jcl = jobcount_local, 
        lfl = logfile_local))

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/log/{fd}.log'.format(fd=filedate)
    
    util.export_to_dropbox.move_to_dropbox(mainpage_local, mainpage_dropbox)
    util.export_to_dropbox.move_to_dropbox(jobcount_local, jobcount_dropbox)
    util.export_to_dropbox.move_to_dropbox(logfile_local, logfile_dropbox)


def test_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'test/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'test/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'test/log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Monster -o "{mainpage_local}" -a test=True -a jobcountfile="{jobcount_local}" -a logfile="{logfile_local}"'.format(mainpage_local = mainpage_local, jobcount_local = jobcount_local, logfile_local = logfile_local))
    

def start_logging(filepath):
    logger = scrapelogger.ScrapeLogger('shine-scraper', logfile)
    
    return logger

if __name__ == '__main__':
    # Default behavior is to run a test
    test_scrape(filedate)
    