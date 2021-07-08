import os
import sys
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import pathlib

# Can't run this file directly - needs to be called from parent folder
from teamlease.teamlease.spiders.TeamLeaseSpider import TeamLeaseSpider
from util.export_to_dropbox import move_to_dropbox
from util.dashboard import update_dashboard_mainpage, update_dashboard_details


def run_full_scrape():

    TL_PATH = pathlib.Path(__file__).parent.resolve()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'teamlease.teamlease.settings'
    
    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = os.path.join(TL_PATH, 'output', 'mainpage', 'teamlease_mainpage_{fd}.csv'.format(fd=filedate))
    jobcount_local = os.path.join(TL_PATH, 'output', 'jobcount', 'teamlease_jobcount_{fd}.csv'.format(fd=filedate))
    mainlogfile_local = os.path.join(TL_PATH, 'log', 'mainpage', '{fd}.log'.format(fd=filedate))

    settings = get_project_settings()
    settings.set('LOG_FILE', mainlogfile_local)
    settings.set('FEED_URI', mainpage_local)
    settings.set('FEED_FORMAT', 'csv')

    process = CrawlerProcess(settings)
    
    process.crawl(TeamLeaseSpider, jobcountfile = jobcount_local, test = False)
    process.start() # the script will block here until the crawling is finished
    
    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/mainpage/teamlease_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/jobcount/teamlease_jobcount_{fd}.csv'.format(fd=filedate)
    mainlogfile_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/log/mainpage/{fd}.log'.format(fd=filedate)
    
    move_to_dropbox(mainpage_local, mainpage_dropbox)
    move_to_dropbox(jobcount_local, jobcount_dropbox)
    move_to_dropbox(mainlogfile_local, mainlogfile_dropbox)

    update_dashboard_mainpage('teamlease', mainpage_local, mainlogfile_local)

def test_scrape():
    
    TL_PATH = pathlib.Path(__file__).parent.resolve()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'teamlease.teamlease.settings'
    
    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = os.path.join(TL_PATH, 'test', 'mainpage', 'teamlease_mainpage_{fd}.csv'.format(fd=filedate))
    jobcount_local = os.path.join(TL_PATH, 'test', 'jobcount', 'teamlease_jobcount_{fd}.csv'.format(fd=filedate))
    logfile_local = os.path.join(TL_PATH, 'test', 'log', '{fd}.log'.format(fd=filedate))

    settings = get_project_settings()
    settings.set('LOG_FILE', logfile_local)
    #settings.set('FEED_URI', mainpage_local)
    #settings.set('FEED_FORMAT', 'csv')
    settings.set('FEEDS', {'file:///' + mainpage_local : {'format' : 'csv'}})

    process = CrawlerProcess(settings)
    
    process.crawl(TeamLeaseSpider, jobcountfile = jobcount_local, test = True)
    process.start() # the script will block here until the crawling is finished


if __name__ == '__main__':
    # File can't be run directly - imports need to be called from parent folder
    pass