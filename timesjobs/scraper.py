import os
import sys

from datetime import datetime

import mainscrape
import detailscrape

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

import util.export_to_dropbox

def run_full_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'output/mainpage/timesjobs_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'output/jobcount/timesjobs_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'log/{fd}.log'.format(fd=filedate)

    mainscrape.run(mainpage_local, jobcount_local, logfile_local)

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/mainpage/timesjobs_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/jobcount/timesjobs_jobcount_{fd}.csv'.format(fd=filedate)

    util.export_to_dropbox.move_to_dropbox(mainpage_local, mainpage_dropbox)
    util.export_to_dropbox.move_to_dropbox(jobcount_local, jobcount_dropbox)

    details_local = 'output/details/timesjobs_details_{fd}.csv'.format(fd=filedate)

    detailscrape.run(mainpage_local, details_local, logfile_local)
    
    details_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/details/timesjobs_details_{fd}.csv'.format(fd=filedate)
    logfile_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/log/{fd}.log'.format(fd=filedate)
    
    util.export_to_dropbox.move_to_dropbox(details_local, details_dropbox)
    util.export_to_dropbox.move_to_dropbox(logfile_local, logfile_dropbox)


def test_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'test/mainpage/timesjobs_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'test/jobcount/timesjobs_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'test/log/{fd}.log'.format(fd=filedate)
    
    mainscrape.run(mainpage_local, jobcount_local, logfile_local, test = True)


if __name__ == '__main__':
    # Default behavior is to run a test
    test_scrape()
    