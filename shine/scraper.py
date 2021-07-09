import os
import sys
import glob

from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import pathlib

# Can't run this file directly - needs to be called from parent folder
from shine.shine.spiders.ShineSpider import ShineSpider
from util.export_to_dropbox import move_to_dropbox
from util.dashboard import update_dashboard_mainpage, update_dashboard_details

import shine.detailscrape

def run_full_scrape():

    SHINE_PATH = pathlib.Path(__file__).parent.resolve()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'shine.shine.settings'

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = os.path.join(SHINE_PATH, 'output', 'mainpage', 'shine_mainpage_{fd}.csv'.format(fd=filedate))
    jobcount_local = os.path.join(SHINE_PATH, 'output', 'jobcount', 'shine_jobcount_{fd}.csv'.format(fd=filedate))
    details_local = os.path.join(SHINE_PATH, 'output', 'details', 'shine_details_{fd}.csv'.format(fd=filedate))
    mainlogfile_local = os.path.join(SHINE_PATH, 'log', 'mainpage', '{fd}.log'.format(fd=filedate))

    settings = get_project_settings()
    settings.set('LOG_FILE', mainlogfile_local)
    settings.set('FEED_URI', mainpage_local)
    settings.set('FEED_FORMAT', 'csv')

    process = CrawlerProcess(settings)
    
    process.crawl(ShineSpider, jobcountfile = jobcount_local, test = False)
    process.start() # the script will block here until the crawling is finished
    
    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/output/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/output/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    details_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/output/details/shine_details_{fd}.csv'.format(fd=filedate)
    mainlogfile_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/log/mainpage/{fd}.log'.format(fd=filedate)
    detaillogfile_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/log/details/{fd}.log'.format(fd=filedate)
        
    move_to_dropbox(mainpage_local, mainpage_dropbox)
    move_to_dropbox(jobcount_local, jobcount_dropbox)
    move_to_dropbox(mainlogfile_local, mainlogfile_dropbox)
    
    update_dashboard_mainpage('shine', mainpage_local, mainlogfile_local)

    detaillogfile_local = os.path.join(SHINE_PATH, 'log', 'details', '{fd}.log'.format(fd=filedate))

    ds = shine.detailscrape.DetailScraper(mainpagefile = mainpage_local,
                       detailsfile = details_local, 
                       logfile = detaillogfile_local)
    ds.run()    
        
    # Move the log and details files
    move_to_dropbox(details_local, details_dropbox)
    move_to_dropbox(detaillogfile_local, detaillogfile_dropbox)

    update_dashboard_details('shine', details_local, detaillogfile_local)


def test_scrape():

    SHINE_PATH = pathlib.Path(__file__).parent.resolve()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'shine.shine.settings'
    
    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = os.path.join(SHINE_PATH, 'test', 'mainpage', 'shine_mainpage_{fd}.csv'.format(fd=filedate))
    jobcount_local = os.path.join(SHINE_PATH, 'test', 'jobcount', 'shine_jobcount_{fd}.csv'.format(fd=filedate))
    details_local = os.path.join(SHINE_PATH, 'test', 'details', 'shine_details_{fd}.csv'.format(fd=filedate))
    logfile_local = os.path.join(SHINE_PATH, 'test', 'log', '{fd}.log'.format(fd=filedate))

    settings = get_project_settings()
    settings.set('LOG_FILE', logfile_local)
    #settings.set('FEED_URI', mainpage_local)
    #settings.set('FEED_FORMAT', 'csv')
    
    settings.set('FEEDS', {'file:///' + mainpage_local : {'format' : 'csv'}})

    process = CrawlerProcess(settings)
    
    process.crawl(ShineSpider, jobcountfile = jobcount_local, test = True)
    process.start() # the script will block here until the crawling is finished

def test_details():

    SHINE_PATH = pathlib.Path(__file__).parent.resolve()

    input_files = glob.glob(os.path.join(SHINE_PATH, 'test', 'mainpage', '*.csv'))
    if input_files:
        latest_input = max(input_files, key=os.path.getctime)
    else:
        raise Exception("No input files detected")

    print('Input file:', latest_input)
    file_ending = latest_input.split('mainpage_')[1]
    mainpage_local = os.path.join(SHINE_PATH, 'test', 'mainpage', latest_input)
    details_local = os.path.join(SHINE_PATH, 'test', 'details', 'shine_details_' + file_ending)
    logfile_local = os.path.join(SHINE_PATH, 'test', 'log', 'detail_scrape.log')
    
    ds = shine.detailscrape.DetailScraper(mainpagefile = mainpage_local,
                       detailsfile = details_local, 
                       logfile = logfile_local, 
                       test = True)
    ds.run()            

if __name__ == '__main__':
    # File can't be run directly - imports need to be called from parent folder
    pass
    