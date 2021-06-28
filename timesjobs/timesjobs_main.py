# -*- coding: utf-8 -*-
"""
    TimesJobs
    Jan 8 2021
    
    Get main page from all cities
    
"""

import requests_html
from requests_html import HTMLSession
import math
import time
import re
from datetime import datetime
import pytz
import csv
import random

import scrapelogger
import sys

import argparse

# Make this the timestamp reflects India timeszone
TZ = pytz.timezone('Asia/Kolkata')

# Use list of realistic headers and rotate between them so that it looks like multiple different users are accessing the site
HEADER_LIST = [
    {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "en,en-US;q=0.9,en;q=0.8", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36", 
    },
    {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
    }
]

def get_header():
    return random.choice(HEADER_LIST)

def get_all_locations(session):
    r = session.get('https://www.timesjobs.com/job-location', headers = get_header())
    lhs = r.html.find('div.lhs')[0]
    links = lhs.find('a')
    locations = [l.attrs['href'] for l in links]
    locations_noduplicates = []
    for elem in locations:
        if elem not in locations_noduplicates:
            locations_noduplicates.append(elem)
    
    return locations_noduplicates

def get_totaljobcount(session, location):
    r = session.get(location, headers = get_header())
    totalcount = r.html.find('#totolResultCountsId')
    return int(totalcount[0].text)

def scrape_row(page_details, job, writer):
    row = {}
    # Full text
    row['text'] = job.text
    
    # Job ID number
    m = re.search('JD_[0-9]+', job.html)
    if m:
        row['id'] = m[0]
    else:
        row['id'] = ''
     
    row['title'] = job.find('h2')[0].text
    row['company'] = job.find('.joblist-comp-name')[0].text
    
    details = job.find('ul.job-more-dtl.clearfix')[0].find('li')
    row['experience'] =  details[0].text
    row['salary'] = details[1].text
    row['location'] = details[2].text
     
    # Link to detail page
    for link in job.links:
        if 'job-detail' in link:
            row['link'] = link
    
    row['locationurl'] = page_details['locationurl']
    row['pageno'] = page_details['pageno']
    
    row['scrapetime'] =datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S")
    
    writer.writerow(row)

def scrape_page(session, location, pageno, writer):
    try:
        r = session.get(location + '/&sequence={}&startPage=1'.format(pageno), headers = get_header())
    except:
        logger.log.warning("Connection reset, waiting for 10 mins")
        time.sleep(60*10)
        r = session.get(location + '/&sequence={}&startPage=1'.format(pageno), headers = get_header())

    jobs = r.html.find('.joblistli')
    
    page_details = {'locationurl' : location, 'pageno' : pageno}
    
    for job in jobs:
        scrape_row(page_details, job, writer)

def main():
    session = HTMLSession()
    if args.debug:
        locations = ['https://www.timesjobs.com/jobs-in-agra/']
    else:
        locations = get_all_locations(session)
    
   
    fmain = open(args.mainpage, 'w', newline =  '')
    fcount = open(args.jobcount, 'w', newline = '')
        
    fmainfields = [
        'text', 'id', 'title', 'company', 'experience', 'salary', 'location', 'link', 'locationurl', 'pageno', 'scrapetime'
        ]
    mainwriter = csv.DictWriter(fmain, fmainfields)
    mainwriter.writeheader()
    
    fcountfields = ['locationurl', 'count']
    countwriter = csv.DictWriter(fcount, fcountfields)
    countwriter.writeheader()
    
    for location in locations:
        if 'simaur' not in location:
            jobcount = get_totaljobcount(session, location)
            countwriter.writerow({'locationurl' : location, 'count' : jobcount})
            pages = math.ceil(jobcount / 50)
            
            for page in range(1, pages + 1):
                logger.log.info("{} - Scraping page {}/{}".format(location, page, pages))
                time.sleep(3)
                scrape_page(session, location, page, mainwriter)
                
    fmain.close()
    fcount.close()

if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mainpage', required = True, help = 'Output file for mainpage scrape')
    parser.add_argument('--jobcount', required = True, help = 'Output file for jobcount scrape')
    parser.add_argument('--debug', action='store_true', default=False,
                        dest='debug',                                 
                        help='Will run a limited scrape for testing') 
    args = parser.parse_args()
    print("Debug Mode:", args.debug)

    # Set up log file
    logger = scrapelogger.ScrapeLogger('TJ-main')

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Include unhandled exceptions in the log file
    sys.excepthook = handle_exception


    # Check types for input files
    mainpage_filetype = args.mainpage.split('.')[-1]
    if mainpage_filetype != 'csv':
        raise Exception('Mainpage file type needs to be csv')
    jobcount_filetype = args.jobcount.split('.')[-1]
    if jobcount_filetype != 'csv':
        raise Exception('Jobcount file type needs to be csv')

    main()
    logger.finalize()

