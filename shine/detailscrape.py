# -*- coding: utf-8 -*-
# Shine - Detail Page Scrape    

from requests_html import HTMLSession
from datetime import datetime, timedelta
import pytz
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

# Make this the timestamp reflects India timeszone'
TZ = pytz.timezone('Asia/Kolkata')


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
        'url', 'status', 'title', 'posted_date', 'vacancies', 'button_text', 'mainskills', 
        'walkin', 'walkin_desc', 'jobdescription', 'department', 'industry', 'skills', 'education', 
        'recruitername', 'recruiteremail', 'recruitertel', 'recruiterdetails_other', 
        'appinsight_label1', 'appinsight_percentage1', 'appinsight_label2', 'appinsight_percentage2', 'appinsight_label3', 'appinsight_percentage3', 
        'similarjobs', 'scrapetime'
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
        self.logger = scrapelogger.ScrapeLogger('shine-details', logfile, level = logging.INFO)

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
                links.update(['http://www.shine.com' + line['url']])
                counter += 1
                if counter > 25:
                    break
        else:
            for line in csvreader:
                links.update(['http://www.shine.com' + line['url']])
            
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

    def get_element(response, css):
        m = response.find(css)
        if m:
            return m[0].text
        else:
            return 'MISSING'


    def scrape_url(self, url):
        
        session = HTMLSession()

        try:
            r = session.get(url, headers = DetailScraper.get_header())
        except:
            # In case the connection is reset - not sure how to specify this correctly.
            self.logger.log.error("While fetching {} connection reset by peer. Taking a break for 1 min...".format(url))
            time.sleep(60)
            r = session.get(url, headers = DetailScraper.get_header())

        try:
            r.html.render()
            response = r.html 

            title = DetailScraper.get_element(response, '.cls_jobtitle')
            top_rhs = response.find('.jobDate')

            posted_date = ''
            vacancies = ''
            for item in top_rhs:
                if 'Posted' in item.text:
                    posted_date = item.text.split('Posted: ')[1]
                elif 'Vacancies' in item.text:
                    vacancies = item.text.split('Vacancies: ')[1]
                    
            if response.find('.walkinlogo'):
                walkin = 'Y'
            else:
                walkin = 'N'

            company = DetailScraper.get_element(response, '.cls_jobcompany')
            experience = DetailScraper.get_element(response, '.cls_jobexperience')
            jobtype = DetailScraper.get_element(response, '.cls_jobType')

            salary = DetailScraper.get_element(response, '.cls_jobsalary')
            locationmain = ', '.join([a.text for a in response.find('.cls_joblocation.cls_jd_primary_location')])
            locationall = DetailScraper.get_element(response, 'div.loc_exp span.socialjdsnippet')
            button_text = DetailScraper.get_element(response, '.yellowbutton')

            mainskills = '; '.join([a.text for a in response.find('div.topbox a.skillanc') if a.text != 'View all'])

            walkindesc = DetailScraper.get_element(response, '.walkinsDesc')
                
            jobdescription = DetailScraper.get_element(response, 'div.jobdescriptioninside')

            jd_details= response.find('div.jobdescription div.sal_fun_ind li')
            department = ''
            industry = ''
            skills = ''
            education = ''

            for row in jd_details:
                if 'Department' in row.text:
                    department = row.text.replace('Department: ', '')
                elif 'Industry' in row.text:
                    industry = row.text.replace('Industry: ', '')
                elif 'Skills' in row.text:
                    skills = ''.join([a.text for a in row.find('.normaljdsnippet')]).replace(',', ';')
                elif 'Education' in row.text:
                    education = row.text.replace('Education ', '')        

            recruiterdetails = DetailScraper.get_element(response, 'div.cls_rect_detail_div')
            recruiteremail = ''
            recruitertel = ''
            recruitername = ''
            recruiterdesc = ''
            recruiterdetails_lines = recruiterdetails.split('\n')
            for row in recruiterdetails.split('\n'):
                if 'Email' in row:
                    recruiteremail = row.replace('Email: ', '')
                    recruiterdetails_lines.remove(row)
                elif 'Telephone' in row:
                    recruitertel = row.replace('Telephone:', '')
                    recruiterdetails_lines.remove(row)
                elif 'Company Name' in row:
                    recruitername = row.replace('Company Name: ', '')
                    recruiterdetails_lines.remove(row)
                    
            recruiterdetails_other = '\n'.join(recruiterdetails_lines)

            # Not reliable - shows one thing on the website, another thing when I
            # view it programatically
            application_status = DetailScraper.get_element(response, '#id_application_insight_heading')
            applicationinsights = response.find('div.ApplicationInsights')[0]
            labels = applicationinsights.find('div.rightSideOther')
            if labels:
                appinsight_label1 = labels[0].text
                appinsight_label2 = labels[1].text
                appinsight_label3 = labels[2].text
            else:
                appinsight_label1 = ''
                appinsight_label2 = ''
                appinsight_label3 = ''
                
            percentages = applicationinsights.find('span.leftSideOther')
            if percentages:
                appinsight_percentage1 = percentages[0].text
                appinsight_percentage2 = percentages[1].text
                appinsight_percentage3 = percentages[2].text
            else:
                appinsight_percentage1 = ''
                appinsight_percentage2 = ''
                appinsight_percentage3 = ''
                
            similarjobslist = response.find('a.cls_searchresult_a')
            similarjobs = '; '.join([item.attrs['data-jobid'] for item in similarjobslist])

            session.close()
            
            return {
                    'url' : url,
                    'status' : 1,
                    'title' : title,
                    'posted_date' : posted_date,
                    'vacancies' : vacancies,
                    'button_text' : button_text,
                    'mainskills' : mainskills,
                    'walkin' : walkin,
                    'walkin_desc' : walkindesc,
                    'jobdescription': jobdescription,
                    'department' : department,
                    'industry' : industry,
                    'skills' : skills,
                    'education' : education,
                    'recruitername' : recruitername,
                    'recruiteremail' : recruiteremail,
                    'recruitertel' : recruitertel,
                    'recruiterdetails_other' : recruiterdetails_other,
                    'appinsight_label1' : appinsight_label1,
                    'appinsight_percentage1' : appinsight_percentage1,
                    'appinsight_label2' : appinsight_label2,
                    'appinsight_percentage2' : appinsight_percentage2,
                    'appinsight_label3' : appinsight_label3,
                    'appinsight_percentage3' : appinsight_percentage3,
                    'similarjobs' : similarjobs,
                    'scrapetime' : datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S")
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
           database = 'shine'
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

    parser = argparse.ArgumentParser(description='Shine Detail Scrape')
    parser.add_argument('--in', help='Infile', required=True)
    parser.add_argument('--out', help='Outfile', required=True)
    parser.add_argument('--log', help='Logfile', required=True)
    args = vars(parser.parse_args())
    
    ds = DetailScraper(args['in'], args['out'], args['log'])
    ds.run()
    
