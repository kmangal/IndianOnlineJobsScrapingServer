import sys

import test.testtasks

import waahjobs.apiscraper
import monster.scraper
import shine.scraper
import timesjobs.scraper
import teamlease.scraper

import timesjobs.detailscrape

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
    
    
if __name__ == '__main__':
    if sys.argv[1] == 'shine':
        shine.scraper.test_scrape()
        