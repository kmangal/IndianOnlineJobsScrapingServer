# -*- coding: utf-8 -*-
# Teamlease - Detail Page Scrape    

from requests_html import HTMLSession
from datetime import datetime, timedelta
import csv
import random
import glob

import time
import sys

import mysql.connector

import sys
import os

import logging

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

from util import scrapelogger

import argparse

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


class DetailScraper:
 
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

    
    fnames = ['url', 'status', 'headertitle', 'jobtype',
                'jobtitle',
                'company',
                'location',
                'exp',
                'salary',
                'edu',
                'applybuttontext',
                'posted_on',
                'job_description',
                'role',
                'timing',
                'process',
                'scrapetime'
                ]

            
    MAX_CONSECUTIVE_ERRORS = 20
    
    def __init__(self, mainpagefile, detailsfile, logfile, test = False):

        # Check types for input files
        mainpage_filetype = mainpagefile.split('.')[-1]
        if mainpage_filetype != 'csv':
            raise Exception('Mainpage file type needs to be csv')
        details_scrape = detailsfile.split('.')[-1]
        if details_scrape != 'csv':
            raise Exception('Details file type needs to be csv')
            

        self.mainpagefile = mainpagefile
        self.detailsfile = detailsfile
        self.logfile = logfile
        
        self.test = test

        # Set up log file
        self.logger = scrapelogger.ScrapeLogger('teamlease-details', logfile, level = logging.INFO)

        self.user_agent_rotator = UserAgent(software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value], 
                                operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value])


        self.consecutiveerrors = 0
        
    def get_user_agent(self):
        return self.user_agent_rotator.get_random_user_agent()
        
    @classmethod
    def get_header(cls):
        return random.choice(cls.HEADER_LIST)

    def get_links(self):
        self.logger.log.info("Pulling links from {}".format(self.mainpagefile))
        f = open(self.mainpagefile, 'r', encoding = 'utf-8')
        csvreader = csv.DictReader(f)
        links = set()

        if self.test:
            counter = 0
            for line in csvreader:
                links.update(['https://www.teamlease.com' + line['url']])
                counter += 1
                if counter > 25:
                    break
        else:
            for line in csvreader:
                links.update(['https://www.teamlease.com' + line['url']])
            
        f.close()
        
        return links
        
    def already_scraped(self, url):
        cursor = self.DB.cursor()
        cursor.execute("SELECT datescraped FROM {} where url = '{}'".format(self.table, url))
        result = cursor.fetchall()
        cursor.close()
        
        if not result:
            return False
        
        for row in result:
            timestamp = row[0]
            if datetime.now() - timestamp  < timedelta(days = 30):
                return True
            
        return False

    def update_database(self, url, status):
        cursor = self.DB.cursor()
        sql = "INSERT INTO {} (url, datescraped, status) VALUES ('{}', '{}', {})".format(self.table, url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), status)
        cursor.execute(sql)
        cursor.close()
        self.DB.commit()

    def get_element(response, css):
        m = response.find(css)
        if m:
            output = ''
            for element in m:
                output += element.text.strip()
            return output
        else:
            return 'MISSING'


    def scrape_url(self, url):
        
        session = HTMLSession()

        tries = 0
        r = None
        
        while not r and tries < 2:          
            try:
                tries += 1
                r = session.get(url, headers = {'User-Agent' : self.get_user_agent()})
            except:
                # In case the connection is reset - not sure how to specify this correctly.
                self.logger.log.warning("Error while fetching {}. Taking a break for 1 min...".format(url))
                time.sleep(60)
        
        if not r:
            session.close()
            return {'url' : url, 'status' : 0}            
            
        try:
            response = r.html
            
            headertitle = DetailScraper.get_element(response, 'h1.header_title')
            
            jobtypeelement = response.find('div.job-type img')
            if jobtypeelement:
                jobtype = jobtypeelement[0].attrs.get('alt', '')
            else:
                jobtype = 'MISSING'
                            
            jobtitle = DetailScraper.get_element(response, 'div.job-display-block h2')            
            company = DetailScraper.get_element(response, 'span.company_name')            
            location = DetailScraper.get_element(response, 'div.location-text')

            topbox = response.find('span.job-display-text')
            exp = ''
            salary = ''
            for element in topbox:
                text = element.text
                if 'Experience' in text:
                    exp = text.replace('Experience', '').replace(':', '').strip()
                elif 'Rs.' in text:
                    salary = text.strip()
                else:
                    pass
                                
            edu = DetailScraper.get_element(response, 'div.course-text')
            applybuttontext = DetailScraper.get_element(response, 'div.top-menu div.apply-button-block')
            posted_on = DetailScraper.get_element(response, 'div.posted').replace('Posted:', '').strip()            
            jd = DetailScraper.get_element(response, 'div.detail-content')

            jobparticularsbox = response.find('div.job-particulars')
            
            role = ''
            timing = ''
            process = ''
            
            if jobparticularsbox:
                for text in jobparticularsbox[0].text.split('\n'):
                    if 'Role' in text:
                        role = text.replace('Role', '').strip()
                    elif 'Job Type' in text:
                        timing = text.replace('Job Type', '').strip()
                    elif 'Hiring Process' in text:
                        process = text.replace('Hiring Process', '').strip()
                    else:
                        pass
                
            session.close()
            
            return {
                'url' : url,
                'status' : 1,
                'headertitle' : headertitle,
                'jobtype' : jobtype,
                'jobtitle' : jobtitle,
                'company' : company,
                'location' : location,
                'exp' : exp,
                'salary' : salary,
                'edu' : edu,
                'applybuttontext' : applybuttontext,
                'posted_on' : posted_on,
                'job_description' : jd,
                'role' : role,
                'timing' : timing,
                'process' : process,
                'scrapetime' : datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }

        except:
            session.close()
            return {'url' : url, 'status' : 0}
        

    def scrape_new_only(self):
        pagecounter = 0
        for link in self.links:
            pagecounter += 1
            if not self.already_scraped(link):
                time.sleep(random.choice(range(1, 4)))
                row = self.scrape_url(link)
                self.writer.writerow(row)
                self.update_database(link, row['status'])
                self.logger.log.info("Page {}/{} {} New Scrape STATUS:{}".format(pagecounter, self.totalpages, link, row['status']))
                if row['status'] == 0 : 
                    self.consecutiveerrors += 1
                else:
                    self.consecutiveerrors = 0
                    
                if self.consecutiveerrors >= DetailScraper.MAX_CONSECUTIVE_ERRORS:
                    self.logger.log.error('Exceeded maximum consecutive errors ({})'.format(self.consecutiveerrors))
                    self.shutdown()
                    return 0
            else:
                self.logger.log.info("Page {}/{} {} Already Scraped".format(pagecounter, self.totalpages, link))

        return 1


    def run(self):

        if self.test:
            self.table = 'test' 
        else:
            self.table = 'history'

        # Connect to database
        self.DB = mysql.connector.connect(
           host="india-labor.citktbvrkzg6.ap-south-1.rds.amazonaws.com",
           user="admin",
           password="b9PR]37DsB",
           database = 'teamlease'
        )

        self.links = self.get_links()
        self.totalpages = len(self.links)

        if os.path.exists(self.detailsfile):
            self.fout = open(self.detailsfile, 'a', newline = '')
            self.writer = csv.DictWriter(self.fout, fieldnames = DetailScraper.fnames)
        else:
            self.fout = open(self.detailsfile, 'a', newline = '')
            self.writer = csv.DictWriter(self.fout, fieldnames = DetailScraper.fnames)
            self.writer.writeheader()  
            
        # Scrape new only
        success = self.scrape_new_only()
        
        if success:           
            self.logger.finalize()


    def shutdown(self):
        self.fout.close()
        self.DB.close()        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Teamlease Detail Scrape')
    parser.add_argument('--in', help='Infile', required=True)
    parser.add_argument('--out', help='Outfile', required=True)
    parser.add_argument('--log', help='Logfile', required=True)
    args = vars(parser.parse_args())
    
    ds = DetailScraper(args['in'], args['out'], args['log'])
    ds.run()
    

