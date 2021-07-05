import os
import sys

from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

#modify_path()

# Can't run this file directly - needs to be called from parent folder
from monster.monster.spiders.MonsterSpider import MonsterSpider
from util.export_to_dropbox import move_to_dropbox


def run_full_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'output/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'output/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'log/{fd}.log'.format(fd=filedate)

    settings = get_project_settings()
    settings.set('LOG_FILE', logfile_local)
    settings.set('FEED_URI', mainpage_local)
    settings.set('FEED_FORMAT', 'csv')

    process = CrawlerProcess(settings)

    process.crawl(MonsterSpider, jobcountfile = jobcount_local, test = False)
    process.start() # the script will block here until the crawling is finished

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_dropbox = '/India Labor Market Indicators/scraping/Monster/ec2/log/{fd}.log'.format(fd=filedate)
    
    move_to_dropbox(mainpage_local, mainpage_dropbox)
    move_to_dropbox(jobcount_local, jobcount_dropbox)
    move_to_dropbox(logfile_local, logfile_dropbox)


def test_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'test/mainpage/monster_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'test/jobcount/monster_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'test/log/{fd}.log'.format(fd=filedate)

    settings = get_project_settings()
    settings.set('LOG_FILE', logfile_local)
    settings.set('FEED_URI', mainpage_local)
    settings.set('FEED_FORMAT', 'csv')

    process = CrawlerProcess(settings)

    process.crawl(MonsterSpider, jobcountfile = jobcount_local, test = True)
    process.start() # the script will block here until the crawling is finished


if __name__ == '__main__':
    pass
    # Default behavior is to run a test
    #test_scrape()
    