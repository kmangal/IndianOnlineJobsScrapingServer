# -*- coding: utf-8 -*-
"""
    Times Jobs - Detail Page Scrape
    
    10 Jan 2021
    
"""

from requests_html import HTMLSession
from datetime import datetime, timedelta
import pytz
import csv
import random
import glob

import time
import sys
import os

import mysql.connector

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

from util import scrapelogger

import argparse

# Make this the timestamp reflects India timeszone'
TZ = pytz.timezone('Asia/Kolkata')


class DetailScraper:

    # Use list of realistic headers and rotate between them so that it looks like multiple different users are accessing the site
    HEADER_LIST = [
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0"}
    ]

    fnames = [
        'url', 'status', 'button_text', 'title', 'company', 'experience', 'salary', 'location', 'posted_on',
        'job_description', 'job_function', 'industry', 'specialization', 'qualification',
        'employment_type', 'role', 'vacancies', 'otherjobinfo', 'skills', 
        'posted_by', 'posted_by_details', 'desired_candidate', 
        'hiring_company', 'hiring_website', 'hiring_industry', 'hiring_turnover', 'hiring_size', 'hiring_other',
        'scrapetime'
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
        self.logger = scrapelogger.ScrapeLogger('TJ-details', logfile)
                
        
    @classmethod
    def get_header():
        return random.choice(DetailScraper.HEADER_LIST)
        
    def get_links(self):
        self.logger.log.info("Pulling links from {}".format(self.mainpagefile))
        f = open(self.mainpagefile, 'r', encoding = 'utf-8')
        csvreader = csv.DictReader(f)
        links = set()

        if self.test:
            counter = 0
            for line in csvreader:
                links.update([line['link']])
                counter += 1
                if counter > 25:
                    break
        else:
            for line in csvreader:
                links.update([line['link']])
            
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
            timestamp = row[0].replace(tzinfo = TZ)
            if datetime.now().astimezone(TZ) - timestamp  < timedelta(days = 30):
                return True
            
        return False

    def update_database(self, url, status):
        cursor = self.DB.cursor()
        sql = "INSERT INTO {} (url, datescraped, status) VALUES ('{}', '{}', {})".format(self.table, url, datetime.now().astimezone(TZ).strftime('%Y-%m-%d %H:%M:%S'), status)
        cursor.execute(sql)
        cursor.close()
        self.DB.commit()

    def scrape_url(self, url):
        
        try:
            r = self.session.get(url, headers = DetailScraper.get_header())
        except:
            # In case the connection is reset - not sure how to specify this correctly.
            self.logger.log.error("While fetching {} connection reset by peer. Taking a break for 1 min...".format(url))
            time.sleep(60)
            r = self.session.get(url, headers = DetailScraper.get_header())

        response = r.html 
        
        try:
            
            # Two types of jobs: regular and walk-in. If walk-in, then the button will say, show interest.
            button_text = response.find('div.top-job-action')[0].text
                
            title = response.find('.jd-job-title')[0].text
            company = response.find('.jd-header.wht-shd-bx > h2')[0].text
            header_details = response.find('ul.top-jd-dtl.clearfix')[0].find('li')
            
            exp = header_details[0].text.replace('card_travel ', '')
            sal = header_details[1].text.replace('₹ ', '')
            loc = header_details[2].text.replace('location_on ', '')
            posted_on = response.xpath('//ul[@class="top-job-insight"]/li/strong[contains(text(), "Posted on")]/text()')[0]
            
            job_desc = response.find('.jd-desc.job-description-main')[0].text
            
            # The info varies across templates
            jobinfo = response.find('div.job-basic-info > ul > li')
            
            # List of possible fields
            job_func = ''
            ind = ''
            spec = ''
            qual = ''
            emp_type = ''
            role = ''
            vacancies = ''
            jobinfoother = ''
            
            for info in jobinfo:
                text = info.text
                if 'Job Function' in text:
                    job_func = text.replace('Job Function:', '').strip()
                elif 'Industry' in text:
                    ind = text.replace('Industry:', '').strip()
                elif 'Specialization' in text:
                    spec = text.replace('Specialization:', '').strip()
                elif 'Qualification' in text:
                    qual = text.replace('Qualification:', '').strip()
                elif 'Employment Type' in text:
                    emp_type = text.replace('Employment Type:', '').strip()
                elif 'Role' in text:
                    role = text.replace('Role:', '').strip()
                elif 'Vacancies' in text:
                    vacancies = text.replace('Vacancies:', '').strip()
                else:
                    jobinfoother = jobinfoother + '\n' + text.strip()
                    
            all_skills = response.find('div.jd-sec.job-skills > div > span > a')
            skills = ', '.join([a.text for a in all_skills])
            
            posted_by_element = response.find('section.job-posted-by > h4')
            if posted_by_element:
                posted_by = posted_by_element[0].text
            else:
                posted_by = ''
                
            posted_by_details_element = response.find('section.job-posted-by > span.posted-content')
            if posted_by_details_element:
                posted_by_details = posted_by_details_element[0].text
            else:
                posted_by_details = ''
                
            desired_candidate_element = response.find('div.jd-sec.dsrd-prof > span > p')
            if desired_candidate_element:
                desired_candidate = "\n".join([a.text for a in desired_candidate_element]).replace('·\xa0', '')
            else:
                desired_candidate = ''
            
            hiring_company_element = response.find('div.jd-sec.jd-hiring-comp > ul > li')
            hiring_company = ''
            hiring_website = ''
            hiring_industry = ''
            hiring_turnover = ''
            hiring_size = ''
            hiring_other = ''
            
            for elem in hiring_company_element:
                text = elem.text
                if 'Company:' in text:
                    hiring_company = text.replace('Company:', '').strip()
                elif 'Website' in text:
                    hiring_website = text.replace('Website', '').strip()
                elif 'Industry' in text:
                    hiring_industry = text.replace('Industry', '').strip()
                elif 'Company Turnover' in text:
                    hiring_turnover = text.replace('Company Turnover', '').strip()
                elif 'Company Size' in text:
                    hiring_size = text.replace('Company Size', '').strip()
                else:
                    hiring_other = hiring_other + '\n' + text.strip()
            
            return {
                    'url': url,
                    'status' : 1,
                    'button_text' : button_text,
                    'title': title,
                    'company': company,
                    'experience': exp,
                    'salary': sal,
                    'location': loc,
                    'posted_on': posted_on,
                    'job_description': job_desc,
                    'job_function': job_func,
                    'industry': ind,
                    'specialization': spec,
                    'qualification': qual,
                    'employment_type': emp_type,
                    'role' : role,
                    'vacancies' : vacancies,
                    'otherjobinfo' : jobinfoother,
                    'skills': skills,
                    'posted_by': posted_by,
                    'posted_by_details': posted_by_details,
                    'desired_candidate' : desired_candidate,
                    'hiring_company' : hiring_company,
                    'hiring_website' : hiring_website,
                    'hiring_industry' : hiring_industry,
                    'hiring_turnover' : hiring_turnover,
                    'hiring_size' : hiring_size,
                    'hiring_other' : hiring_other,
                    'scrapetime' : datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S")
                }    
        
        except:
            return {'url' : url, 'status' : 0}
            

    # def scrape_all(DB, table, session, writer, links, TOTALPAGES):
        # pagecounter = 0
        # for link in links:
            # pagecounter += 1
            # time.sleep(random.choice(range(3, 8)))
            # row = scrape_url(session, link)
            # writer.writerow(row)
            # update_database(DB, table, link, row['status'])
            # logger.log.info("Page {}/{} - {} - New Scrape - STATUS:{}".format(pagecounter, TOTALPAGES, link, row['status']))

    def scrape_new_only(self):
        pagecounter = 0
        for link in self.links:
            pagecounter += 1
            if not self.already_scraped(link):
                time.sleep(random.choice(range(1, 16)))
                row = self.scrape_url(link)
                self.writer.writerow(row)
                self.update_database(self, link, row['status'])
                self.logger.log.info("Page {}/{} - {} - New Scrape - STATUS:{}".format(pagecounter, self.totalpages, link, row['status']))
            else:
                self.logger.log.info("Page {}/{} - {} - Already Scraped".format(pagecounter, self.totalpages, link))


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
           database = 'timesjobs'
        )

        self.session = HTMLSession()

        self.links = self.get_links()
        self.totalpages = len(self.links)

        fout = open(self.detailsfile, 'w', newline = '')

        self.writer = csv.DictWriter(fout, fieldnames = DetailScraper.fnames)
        self.writer.writeheader()
        
        # Scrape new only
        self.scrape_new_only()
            
        fout.close()
        self.DB.close()

        self.logger.finalize()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='DetailScrape')
    parser.add_argument('--in', help='Infile', required=True)
    parser.add_argument('--out', help='Outfile', required=True)
    parser.add_argument('--log', help='Logfile', required=True)
    args = vars(parser.parse_args())
    
    ds = DetailScraper(args['in'], args['out'], args['log'])
    ds.run()
    