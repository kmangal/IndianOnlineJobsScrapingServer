# -*- coding: utf-8 -*-
# Monster - Detail Page Scrape    

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


    fnames = [
        'url', 'status', 'jobid', 'jobtitle', 'company', 'location', 'exp', 'package', 'jobtype', 'posted_on', 'totalviews', 
        'totalapplications', 'job_description', 'employment_type', 'industry', 'function', 'roles', 'last_updated', 'scrapetime'
        ]
            
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
        self.logger = scrapelogger.ScrapeLogger('monster-details', logfile, level = logging.INFO)

        self.user_agent_rotator = UserAgent(software_names=[SoftwareName.CHROME.value, SoftwareName.FIREFOX.value], 
                                operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value])

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
                links.update([line['url']])
                counter += 1
                if counter > 25:
                    break
        else:
            for line in csvreader:
                links.update([line['url']])
            
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

        try:
            r = session.get(url, headers = {'User-Agent' : self.get_user_agent()})
        except:
            # In case the connection is reset - not sure how to specify this correctly.
            self.logger.log.warning("While fetching {} connection reset by peer. Taking a break for 1 min...".format(url))
            time.sleep(60)
            r = session.get(url, headers = {'User-Agent' : self.get_user_agent()})

        try:
            r.html.render()
            response = r.html 
            
            jobtitle = DetailScraper.get_element(response, 'div.detail-job-tittle > h1')            
            company = DetailScraper.get_element(response, 'div.detail-job-tittle > span')            
            location = DetailScraper.get_element(response, 'div.detail-job-tittle span.loc')             
            exp = DetailScraper.get_element(response, 'div.job-tittle-box div.exp')             
            package = DetailScraper.get_element(response, 'span.package')            
            jobtype = DetailScraper.get_element(response, 'div.posted-update > span.color-grey-light')

            posted_stats = response.find('span.posted')
            
            posted_on = ''
            totalviews= ''
            totalapplications = ''
            jobid = ''
            
            for element in posted_stats:
                text = element.text
                if 'Posted On:' in text:
                    posted_on = text.replace('Posted On:', '').strip()
                elif 'Total Views:' in text:
                    # Needs javascript
                    totalviews = text.replace('Total Views:', '').strip()
                elif 'Total Applications :' in text:
                    totalapplications = text.replace('Total Applications :', '').strip()
                elif 'Job Id:' in text:
                    jobid = text.replace('Job Id:', '').strip()
                else:
                   pass
   

            jd = DetailScraper.get_element(response, 'div.jd-text')
            
            detail_list = response.find('div.job-detail-list')
            
            employment_type = ''
            industry = ''
            function = ''
            roles = ''
            
            for row in detail_list:
                text = row.text
                if 'Employment Types:' in text:
                    employment_type = text.replace('Employment Types:', '').strip()
                elif 'Industry:' in text:
                    industry = text.replace('Industry:', '').strip()
                elif 'Function:' in text:
                    function = text.replace('Function:', '').strip()
                elif 'Roles:' in text:
                    roles = text.replace('Roles:', '').strip()
                else:
                    pass
            
            # Needs javascript
            last_updated = DetailScraper.get_element(response, 'div.last-updated')

            session.close()
            
            return {
                'url' : url,
                'status' : 1,
                'jobid' : jobid,
                'jobtitle' : jobtitle,
                'company' : company,
                'location' : location,
                'exp' : exp,
                'package' : package,
                'jobtype' : jobtype,
                'posted_on' : posted_on,
                'totalviews' : totalviews,
                'totalapplications' : totalapplications,
                'job_description' : jd,
                'employment_type' : employment_type,
                'industry' : industry,
                'function' : function,
                'roles' : roles,
                'last_updated' : last_updated,
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
            else:
                self.logger.log.info("Page {}/{} {} Already Scraped".format(pagecounter, self.totalpages, link))


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
           database = 'monster'
        )

        self.links = self.get_links()
        self.totalpages = len(self.links)

        if os.path.exists(self.detailsfile):
            fout = open(self.detailsfile, 'a', newline = '')
            self.writer = csv.DictWriter(fout, fieldnames = DetailScraper.fnames)
        else:
            fout = open(self.detailsfile, 'a', newline = '')
            self.writer = csv.DictWriter(fout, fieldnames = DetailScraper.fnames)
            self.writer.writeheader()  
            
            
        # Scrape new only
        self.scrape_new_only()
            
        fout.close()
        self.DB.close()
        
        self.logger.finalize()



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Monster Detail Scrape')
    parser.add_argument('--in', help='Infile', required=True)
    parser.add_argument('--out', help='Outfile', required=True)
    parser.add_argument('--log', help='Logfile', required=True)
    args = vars(parser.parse_args())
    
    ds = DetailScraper(args['in'], args['out'], args['log'])
    ds.run()
    

