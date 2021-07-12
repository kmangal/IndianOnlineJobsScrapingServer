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

import teamlease.detailscrape


def mainpage_scrape(filedate):
   
    TL_PATH = pathlib.Path(__file__).parent.resolve()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'teamlease.teamlease.settings'
    
    mainpage_local = os.path.join(TL_PATH, 'output', 'mainpage', 'teamlease_mainpage_{fd}.csv'.format(fd=filedate))
    jobcount_local = os.path.join(TL_PATH, 'output', 'jobcount', 'teamlease_jobcount_{fd}.csv'.format(fd=filedate))
    mainlogfile_local = os.path.join(TL_PATH, 'log', 'mainpage', '{fd}.log'.format(fd=filedate))

    settings = get_project_settings()
    settings.set('LOG_FILE', mainlogfile_local)
    settings.set('FEED_URI', mainpage_local)
    settings.set('FEED_FORMAT', 'csv')

    process = CrawlerProcess(settings)
    
    process.crawl(TeamLeaseSpider, jobcountfile = jobcount_local, test = False)
    
    try:
        process.start() # the script will block here until the crawling is finished
    except:
        pass
    
    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/output/mainpage/teamlease_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/output/jobcount/teamlease_jobcount_{fd}.csv'.format(fd=filedate)
    mainlogfile_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/log/mainpage/{fd}.log'.format(fd=filedate)
    
    if os.path.isfile(mainpage_local):
        move_to_dropbox(mainpage_local, mainpage_dropbox)
    
    if os.path.isfile(jobcount_local):
        move_to_dropbox(jobcount_local, jobcount_dropbox)
    
    if os.path.isfile(mainlogfile_local):
        move_to_dropbox(mainlogfile_local, mainlogfile_dropbox)

    update_dashboard_mainpage('teamlease', mainpage_local, mainlogfile_local)
    
    
def details_scrape(filedate):
    
    TL_PATH = pathlib.Path(__file__).parent.resolve()

    mainpage_local = os.path.join(TL_PATH, 'output', 'mainpage', 'teamlease_mainpage_{fd}.csv'.format(fd=filedate))
    details_local = os.path.join(TL_PATH, 'output', 'details', 'teamlease_details_{fd}.csv'.format(fd=filedate))
    detaillogfile_local = os.path.join(TL_PATH, 'log', 'details', '{fd}.log'.format(fd=filedate))

    ds = teamlease.detailscrape.DetailScraper(mainpagefile = mainpage_local,
                       detailsfile = details_local, 
                       logfile = detaillogfile_local)
    
    try:
        ds.run()    
    except:
        pass
    
    details_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/output/details/teamlease_details_{fd}.csv'.format(fd=filedate)
    detaillogfile_dropbox = '/India Labor Market Indicators/scraping/TeamLease/ec2/log/details/{fd}.log'.format(fd=filedate)

    # Move the log and details files
    if os.path.isfile(details_local):
        move_to_dropbox(details_local, details_dropbox)
    
    if os.path.isfile(detaillogfile_local):
        move_to_dropbox(detaillogfile_local, detaillogfile_dropbox)

    update_dashboard_details('teamlease', details_local, detaillogfile_local)


def run_full_scrape():
    
    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')
    mainpage_scrape(filedate)
    details_scrape(filedate)

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