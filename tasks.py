import test.testtasks

import waahjobs.apiscraper
import monster.scraper
import shine.scraper

def test_print(message):
    test.testtasks.test_print(message)

def waahjobs_scrape(test):
    waahjobs.apiscraper.run_scrape(test)

def monster_scrape():
    monster.scraper.run_full_scrape()
    
def shine_scrape():
    shine.scraper.run_full_scrape()
    