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
sys.path.append('../')
import util.scrapelogger as scrapelogger

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
            links.update(['http://www.shine.com' + line['url']])
            counter += 1
            if counter > 25:
                break
    else:
        for line in csvreader:
            links.update(['http://www.shine.com' + line['url']])
        
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

def get_element(response, css):
    m = response.find(css)
    if m:
        return m[0].text
    else:
        return 'MISSING'


def scrape_url(session, url):
    
    try:
        r = session.get(url, headers = get_header())
    except:
        # In case the connection is reset - not sure how to specify this correctly.
        logger.log.error("While fetching {} connection reset by peer. Taking a break for 10 mins...".format(url))
        time.sleep(600)
        r = session.get(url, headers = get_header())

    try:
        r.html.render()
        response = r.html 

        title = get_element(response, '.cls_jobtitle')
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

        company = get_element(response, '.cls_jobcompany')
        experience = get_element(response, '.cls_jobexperience')
        jobtype = get_element(response, '.cls_jobType')

        salary = get_element(response, '.cls_jobsalary')
        locationmain = ', '.join([a.text for a in response.find('.cls_joblocation.cls_jd_primary_location')])
        locationall = get_element(response, 'div.loc_exp span.socialjdsnippet')
        button_text = get_element(response, '.yellowbutton')

        mainskills = '; '.join([a.text for a in response.find('div.topbox a.skillanc') if a.text != 'View all'])

        walkindesc = get_element(response, '.walkinsDesc')
            
        jobdescription = get_element(response, 'div.jobdescriptioninside')

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

        recruiterdetails = get_element(response, 'div.cls_rect_detail_div')
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
        application_status = get_element(response, '#id_application_insight_heading')
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



def run_scrape(inputfile, outputfile, logfile, allflag = False, testflag = False):

    logger = scrapelogger.ScrapeLogger('shine-details', logfile)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Include unhandled exceptions in the log file
    sys.excepthook = handle_exception

    if testflag:
        table = 'test' 
    else:
        table = 'history'

    # Connect to database
    DB = mysql.connector.connect(
       host="india-labor.citktbvrkzg6.ap-south-1.rds.amazonaws.com",
       user="admin",
       password="b9PR]37DsB",
       database = 'shine'
    )

    session = HTMLSession()

    links = get_links(inputfile, testflag)
    TOTALPAGES = len(links)

    fout = open(outputfile, 'w', newline = '')

    fnames = [
        'url', 'status', 'title', 'posted_date', 'vacancies', 'button_text', 'mainskills', 
        'walkin', 'walkin_desc', 'jobdescription', 'department', 'industry', 'skills', 'education', 
        'recruitername', 'recruiteremail', 'recruitertel', 'recruiterdetails_other', 
        'appinsight_label1', 'appinsight_percentage1', 'appinsight_label2', 'appinsight_percentage2', 'appinsight_label3', 'appinsight_percentage3', 
        'similarjobs', 'scrapetime'
        ]

    writer = csv.DictWriter(fout, fieldnames = fnames)
    writer.writeheader()

    if allflag:
        scrape_all(DB, table, session, writer, links, TOTALPAGES)
    else:
        scrape_new_only(DB, table, session, writer, links, TOTALPAGES)
        
    fout.close()
    DB.close()


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required = True, help = 'File path for mainpage input')
    parser.add_argument('--output', required = True, help = 'File path for output')
    parser.add_argument('--log', required = True, help = 'File path for log')
    parser.add_argument('--all', action='store_true', default=False,
                        dest='scrape_all',
                        help='Scrape all listings from main page')
    parser.add_argument('--test', action = 'store_true', default = False, 
                        dest = 'test', 
                        help = 'Test run / does not write to database')

    args = parser.parse_args()    
    inputfile = args.input
    outputfile = args.output
    logfile = args.log
    allflag = args.scrape_all
    testflag = args.test
    
    print("Test Mode", testflag)

    run_scrape(inputfile, outputfile, logfile, allflag, testflag)
    logger.finalize()
