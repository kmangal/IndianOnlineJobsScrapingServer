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
import csv
import random

import sys
import os

import random

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()


from util import scrapelogger

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


class MainpageScraper:
        
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

    fmainfields = [
            'text', 'id', 'title', 'company', 'experience', 'salary', 'location', 'link', 'locationurl', 'pageno', 'scrapetime'
            ]
    
    fcountfields = ['locationurl', 'count']


    def __init__(self, mainpagefile, jobcountfile, logfile, test = False):
        
        # Check types for input files
        mainpage_filetype = mainpagefile.split('.')[-1]
        if mainpage_filetype != 'csv':
            raise Exception('Mainpage file type needs to be csv')
        jobcount_filetype = jobcountfile.split('.')[-1]
        if jobcount_filetype != 'csv':
            raise Exception('Jobcount file type needs to be csv')
            
        self.mainpagefile = mainpagefile
        self.jobcountfile = jobcountfile
        self.logfile = logfile
        self.test = test
        
        # Set up log file
        self.logger = scrapelogger.ScrapeLogger('TJ-main', logfile)

        self.user_agent_rotator = UserAgent(software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value], 
                                operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value])

    
    def get_user_agent(self):
        return self.user_agent_rotator.get_random_user_agent()
        
    def get_header():
        return random.choice(MainpageScraper.HEADER_LIST)
    
    def get_all_locations(self):
        r = self.session.get('https://www.timesjobs.com/job-location', headers = {'User-Agent' : self.get_user_agent()})
        lhs = r.html.find('div.lhs')[0]
        links = lhs.find('a')
        locations = [l.attrs['href'] for l in links]
        locations_noduplicates = []
        for elem in locations:
            if elem not in locations_noduplicates:
                locations_noduplicates.append(elem)
        
        return locations_noduplicates
    
    def get_totaljobcount(self, location):
        r = self.session.get(location, headers = {'User-Agent' : self.get_user_agent()})
        totalcount = r.html.find('#totolResultCountsId')
        return int(totalcount[0].text)
    
    def scrape_row(self, page_details, job):
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
        
        row['scrapetime'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        self.writer.writerow(row)
    
    def scrape_page(self, location, pageno):
                
        try:
            r = self.session.get(location + '/&sequence={}&startPage=1'.format(pageno), headers = {'User-Agent' : self.get_user_agent()})
        except:
            self.logger.log.warning("Error establishing connection. Taking a break for 5 mins")
            time.sleep(60*5)
            r = self.session.get(location + '/&sequence={}&startPage=1'.format(pageno), headers = {'User-Agent' : self.get_user_agent()})
    
        jobs = r.html.find('.joblistli')
        
        page_details = {'locationurl' : location, 'pageno' : pageno}
        
        for job in jobs:
            self.scrape_row(page_details, job)
    
    def run(self):
                        
        self.session = HTMLSession()
        
        if self.test:
            self.locations = ['https://www.timesjobs.com/jobs-in-agra/']
        else:
            self.locations = self.get_all_locations()
        
        existingmainfile = os.path.exists(self.mainpagefile)
            
        self.fmain = open(self.mainpagefile, 'a', newline = '')
        self.mainwriter = csv.DictWriter(self.fmain, fieldnames = MainpageScraper.fmainfields)
        if not existingmainfile: self.mainwriter.writeheader()  

        existingcountfile = os.path.exists(self.jobcountfile)
        
        self.fcount = open(self.jobcountfile, 'a', newline = '')
        self.countwriter = csv.DictWriter(self.fcount, MainpageScraper.fcountfields)
        if not existingcountfile : self.countwriter.writeheader()
        
        for location in self.locations:
            if 'simaur' not in location:
                jobcount = self.get_totaljobcount(location)
                self.countwriter.writerow({'locationurl' : location, 'count' : jobcount})
                pages = math.ceil(jobcount / 50)
                
                for page in range(1, pages + 1):
                    self.logger.log.info("{} - Scraping page {}/{}".format(location, page, pages))
                    time.sleep(random.randint(1, 3))
                    self.scrape_page(location, page)
                    
        self.fmain.close()
        self.fcount.close()
    
        self.logger.finalize()

if __name__ == '__main__':
    # Default is to run a test - will implement later
    pass

