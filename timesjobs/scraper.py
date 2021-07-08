import os
import sys

from datetime import datetime

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

import timesjobs.mainscrape
import timesjobs.detailscrape

from util.export_to_dropbox import move_to_dropbox
from util.dashboard import update_dashboard_mainpage, update_dashboard_details


def run_full_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = os.path.expanduser('~/jobs_scraping/timesjobs/output/mainpage/timesjobs_mainpage_{fd}.csv'.format(fd=filedate))
    jobcount_local = os.path.expanduser('~/jobs_scraping/timesjobs/output/jobcount/timesjobs_jobcount_{fd}.csv'.format(fd=filedate))
    mainlogfile_local = os.path.expanduser('~/jobs_scraping/timesjobs/log/{fd}.log'.format(fd=filedate))

    timesjobs.mainscrape.run(mainpage_local, jobcount_local, mainlogfile_local)

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/mainpage/timesjobs_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/jobcount/timesjobs_jobcount_{fd}.csv'.format(fd=filedate)
    mainlogfile_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/log/mainpage/{fd}.log'.format(fd=filedate)

    move_to_dropbox(mainpage_local, mainpage_dropbox)
    move_to_dropbox(jobcount_local, jobcount_dropbox)
    move_to_dropbox(mainlogfile_local, mainlogfile_dropbox)

    update_dashboard_mainpage('timesjobs', mainpage_local, mainlogfile_local)

    details_local = os.path.expanduser('~/job_scraping/timesjobs/output/details/timesjobs_details_{fd}.csv'.format(fd=filedate))
    detailslog_local = os.path.expanduser('~/job_scraping/timesjobs/log/details/{fd}.csv'.format(fd=filedate))

    timesjobs.detailscrape.run(mainpage_local, details_local, detailslog_local)
    
    details_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/details/timesjobs_details_{fd}.csv'.format(fd=filedate)
    detailslog_dropbox = '/India Labor Market Indicators/scraping/TimesJobs/ec2/log/{fd}.log'.format(fd=filedate)
    
    move_to_dropbox(details_local, details_dropbox)
    move_to_dropbox(detailslog_local, detailslog_dropbox)

    update_dashboard_details('timesjobs', details_local, detailslog_local)

def test_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = os.path.expanduser('~/jobs_scraping/timesjobs/test/mainpage/timesjobs_mainpage_{fd}.csv'.format(fd=filedate))
    jobcount_local = os.path.expanduser('~/jobs_scraping/timesjobs/test/jobcount/timesjobs_jobcount_{fd}.csv'.format(fd=filedate))
    logfile_local = os.path.expanduser('~/jobs_scraping/timesjobs/test/log/{fd}.log'.format(fd=filedate))
    
    timesjobs.mainscrape.run(mainpage_local, jobcount_local, logfile_local, test = True)


if __name__ == '__main__':
    # Default behavior is to run a test
    test_scrape()
    