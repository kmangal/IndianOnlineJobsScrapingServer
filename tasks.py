import os
import sys
import glob
import re

import test.testtasks

import waahjobs.apiscraper
import monster.scraper
import shine.scraper
import timesjobs.scraper
import teamlease.scraper

import timesjobs.detailscrape
import shine.detailscrape
import monster.detailscrape

from util.export_to_dropbox import move_to_dropbox
from util.cleanfolder import Cleaner

from util.dashboard import update_dashboard_details

# ---------------------------------------------------
# Helper

FILESUFFIXRE = re.compile(r'\d{8}_\d{6}')

def get_latest_suffix(folder):

    list_of_files = glob.glob(os.path.join(folder, "*.csv"))
    latest_file = max(list_of_files, key=os.path.getctime)

    m = FILESUFFIXRE.search(latest_file)
    
    if m:
        filesuffix = m.group()
    else:
        raise Exception("File name not in expected format")
        
    return filesuffix

# ----------------------------------------------------

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
    

def clean():

    cleaner = Cleaner()
    
    # Shine
    cleaner.clean_folder(
        os.path.expanduser('~/jobs_scraping/shine'),
        '/India Labor Market Indicators/scraping/Shine/ec2'
    )
    
    # Monster
    cleaner.clean_folder(
        os.path.expanduser('~/jobs_scraping/monster'),
        '/India Labor Market Indicators/scraping/Monster/ec2'
    )

    # Timesjobs
    cleaner.clean_folder(
        os.path.expanduser('~/jobs_scraping/timesjobs'),
        '/India Labor Market Indicators/scraping/TimesJobs/ec2'
    )    

    # TeamLease
    cleaner.clean_folder(
        os.path.expanduser('~/jobs_scraping/teamlease'),
        '/India Labor Market Indicators/scraping/TeamLease/ec2'
    )   

    # WaahJobs
    cleaner.clean_folder(
        os.path.expanduser('~/jobs_scraping/waahjobs'),
        '/India Labor Market Indicators/scraping/WaahJobs/ec2'
    )  

    cleaner.close()
    

# ---------------------------------------------------------------------------
# Special tasks

def timesjobs_detail_scrape(**kwargs):
    ds = timesjobs.detailscrape.DetailScraper(kwargs['infile'], kwargs['outfile'], kwargs['log'])
    ds.run()

def shine_detail_scrape(**kwargs):
    SHINE_PATH = os.path.expanduser('~/jobs_scraping/shine')
    mainpage_local = os.path.join(SHINE_PATH, 'output', 'mainpage', kwargs['infile'])
    details_local = os.path.join(SHINE_PATH, 'output', 'details', kwargs['outfile'])
    logfile_local = os.path.join(SHINE_PATH, 'log', 'details', kwargs['log'])
    
    ds = shine.detailscrape.DetailScraper(mainpage_local, details_local, logfile_local)
    ds.run()
    
    details_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/output/details/{f}'.format(f=kwargs['outfile'])
    logfile_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/log/details/{f}'.format(f=kwargs['log'])
    
    move_to_dropbox(details_local, details_dropbox)
    move_to_dropbox(logfile_local, logfile_dropbox)
    
    
def monster_detail_scrape():
    
    filesuffix = get_latest_suffix(os.path.expanduser('~/jobs_scraping/monster/output/mainpage'))
    
    MONSTER_PATH = os.path.expanduser('~/jobs_scraping/monster')
    mainpage_local = os.path.join(MONSTER_PATH, 'output', 'mainpage', 'monster_mainpage_{}.csv'.format(filesuffix))
    details_local = os.path.join(MONSTER_PATH, 'output', 'details', 'monster_details_{}.csv'.format(filesuffix))
    logfile_local = os.path.join(MONSTER_PATH, 'log', 'details', '{}.log'.format(filesuffix))
    
    ds = monster.detailscrape.DetailScraper(mainpage_local, details_local, logfile_local)
    ds.run()
    
    details_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/output/details/monster_details_{f}.csv'.format(filesuffix)
    logfile_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/log/details/{}.log'.format(filesuffix)
    
    move_to_dropbox(details_local, details_dropbox)
    move_to_dropbox(logfile_local, logfile_dropbox)

    update_dashboard_details('monster', details_local, logfile_local)

def teamlease_detail_scrape():
    filesuffix = get_latest_suffix(os.path.expanduser('~/jobs_scraping/teamlease/output/mainpage'))
    teamlease.scraper.details_scrape(filesuffix)
    

if __name__ == '__main__':

    if sys.argv[1] == 'shine':
        shine.scraper.test_scrape()
    elif sys.argv[1] == 'teamlease':
        teamlease.scraper.test_scrape()
    elif sys.argv[1] == 'shine-detail':
        shine.scraper.test_details()
    elif sys.argv[1] == 'monster-detail':
        monster_detail_scrape()
    elif sys.argv[1] == 'clean':
        clean()
    else:
        print("Argument not recognized")