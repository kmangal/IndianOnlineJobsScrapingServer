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

import mysql.connector

import timesjobs.scrapelogger
import argparse


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

# Make this the timestamp reflects India timeszone'
TZ = pytz.timezone('Asia/Kolkata')


def get_header():
    return random.choice(HEADER_LIST)
        
def get_links(infile, debug = False):
    logger.log.info("Pulling links from {}".format(infile))
    f = open(infile, 'r', encoding = 'utf-8')
    csvreader = csv.DictReader(f)
    links = set()

    if debug:
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

def already_scraped(DB, table, url):
    cursor = DB.cursor()
    cursor.execute("SELECT datescraped FROM {} where url = '{}'".format(table, url))
    result = cursor.fetchall()
    cursor.close()
    
    if not result:
        return False
    
    for row in result:
        timestamp = row[0].replace(tzinfo = TZ)
        if datetime.now().astimezone(TZ) - timestamp  < timedelta(days = 30):
            return True
        
    return False

def update_database(DB, table, url, status):
    cursor = DB.cursor()
    sql = "INSERT INTO {} (url, datescraped, status) VALUES ('{}', '{}', {})".format(table, url, datetime.now().astimezone(TZ).strftime('%Y-%m-%d %H:%M:%S'), status)
    cursor.execute(sql)
    cursor.close()
    DB.commit()

def scrape_url(session, url):
    
    try:
        r = session.get(url, headers = get_header())
    except:
        # In case the connection is reset - not sure how to specify this correctly.
        logger.log.error("While fetching {} connection reset by peer. Taking a break for 10 mins...".format(url))
        time.sleep(600)
        r = session.get(url, headers = get_header())

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
        

def scrape_all(DB, table, session, writer, links, TOTALPAGES):
    pagecounter = 0
    for link in links:
        pagecounter += 1
        time.sleep(random.choice(range(3, 8)))
        row = scrape_url(session, link)
        writer.writerow(row)
        update_database(DB, table, link, row['status'])
        logger.log.info("Page {}/{} - {} - New Scrape - STATUS:{}".format(pagecounter, TOTALPAGES, link, row['status']))

def scrape_new_only(DB, table, session, writer, links, TOTALPAGES):
    pagecounter = 0
    for link in links:
        pagecounter += 1
        if not already_scraped(DB, table, link):
            time.sleep(random.choice(range(1, 16)))
            row = scrape_url(session, link)
            writer.writerow(row)
            update_database(DB, table, link, row['status'])
            logger.log.info("Page {}/{} - {} - New Scrape - STATUS:{}".format(pagecounter, TOTALPAGES, link, row['status']))
        else:
            logger.log.info("Page {}/{} - {} - Already Scraped".format(pagecounter, TOTALPAGES, link))



def main():

    if args.debug:
        table = 'test' 
    else:
        table = 'history'

    # Connect to database
    DB = mysql.connector.connect(
       host="india-labor.citktbvrkzg6.ap-south-1.rds.amazonaws.com",
       user="admin",
       password="b9PR]37DsB",
       database = 'timesjobs'
    )

    session = HTMLSession()

    links = get_links(args.input, args.debug)
    TOTALPAGES = len(links)

    fout = open(args.output, 'w', newline = '')

    fnames = [
        'url', 'status', 'button_text', 'title', 'company', 'experience', 'salary', 'location', 'posted_on',
        'job_description', 'job_function', 'industry', 'specialization', 'qualification',
        'employment_type', 'role', 'vacancies', 'otherjobinfo', 'skills', 
        'posted_by', 'posted_by_details', 'desired_candidate', 
        'hiring_company', 'hiring_website', 'hiring_industry', 'hiring_turnover', 'hiring_size', 'hiring_other',
        'scrapetime'
        ]

    writer = csv.DictWriter(fout, fieldnames = fnames)
    writer.writeheader()

    if args.scrape_all:
        scrape_all(DB, table, session, writer, links, TOTALPAGES)
    else:
        scrape_new_only(DB, table, session, writer, links, TOTALPAGES)
        
    fout.close()
    DB.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required = True, help = 'File path for mainpage intput')
    parser.add_argument('--output', required = True, help = 'File path for output')
    parser.add_argument('--all', action='store_true', default=False,
                        dest='scrape_all',
                        help='Scrape all listings from main page')
    parser.add_argument('--debug', action = 'store_true', default = False, 
                        dest = 'debug', 
                        help = 'Test run / does not write to database')

    logger = timesjobs.scrapelogger.ScrapeLogger('TJ-details')

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Include unhandled exceptions in the log file
    sys.excepthook = handle_exception

    args = parser.parse_args()
    print("Debug Mode", args.debug)

    main()
    logger.finalize()
