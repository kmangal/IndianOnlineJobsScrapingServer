import os
import sys

import test.testtasks

import waahjobs.apiscraper
import monster.scraper
import shine.scraper
import timesjobs.scraper
import teamlease.scraper

import timesjobs.detailscrape
import shine.detailscrape

from util.export_to_dropbox import move_to_dropbox


def test_print(message):
    test.testtasks.test_print(message)

def waahjobs_scrape(test):
    waahjobs.apiscraper.run_scrape(test)

def monster_scrape():
    monster.scraper.run_full_scrape()
    
def shine_scrape():
    shine.scraper.run_full_scrape()

def timesjobs_scrape():
    timesjobs.scraper.run_full_scrape()
    
def teamlease_scrape():
    teamlease.scraper.run_full_scrape()
    

# Special tasks

def timesjobs_detail_scrape(**kwargs):
    ds = timesjobs.detailscrape.DetailScraper(kwargs['infile'], kwargs['outfile'], kwargs['log'])
    ds.run()

def shine_detail_scrape(**kwargs):
    SHINE_PATH = os.path.expanduser('~/jobs_scraping/shine')
    mainpage_local = os.path.join(SHINE_PATH, 'output', 'mainpage', kwargs['infile'])
    details_local = os.path.join(SHINE_PATH, 'output', 'details', kwargs['outfile'])
    logfile_local = os.path.join(SHINE_PATH, 'log', kwargs['log'])
    
    ds = shine.detailscrape.DetailScraper(mainpage_local, details_local, logfile_local)
    ds.run()
    
    details_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/details/{f}'.format(f=kwargs['outfile'])
    logfile_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/log/{f}'.format(f=kwargs['log'])
    
    move_to_dropbox(details_local, details_dropbox)
    move_to_dropbox(logfile_local, logfile_dropbox)
    
if __name__ == '__main__':

    if sys.argv[1] == 'shine':
        shine.scraper.test_scrape()
    elif sys.argv[1] == 'teamlease':
        teamlease.scraper.test_scrape()
        