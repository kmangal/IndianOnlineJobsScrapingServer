import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import re
import time
import csv
import pytz
import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC 

CHROMEDRIVER_PATH = '/home/ec2-user/naukri/chromedriver'

EXCEPTIONS = set([
    'https://www.naukri.com/jobs-in-andhra-pradesh',
    'https://www.naukri.com/jobs-in-arunachal-pradesh',
    'https://www.naukri.com/jobs-in-assam',
    'https://www.naukri.com/jobs-in-bihar',
    'https://www.naukri.com/jobs-in-chhattisgarh',
    'https://www.naukri.com/jobs-in-goa',
    'https://www.naukri.com/jobs-in-gujrat',
    'https://www.naukri.com/jobs-in-haryana',
    'https://www.naukri.com/jobs-in-himachal-pradesh',
    'https://www.naukri.com/jobs-in-jammu-and-kashmir',
    'https://www.naukri.com/jobs-in-jharkhand',
    'https://www.naukri.com/jobs-in-karnataka',
    'https://www.naukri.com/jobs-in-kerala',
    'https://www.naukri.com/jobs-in-madhya-pradesh',
    'https://www.naukri.com/jobs-in-maharashtra',
    'https://www.naukri.com/jobs-in-manipur',
    'https://www.naukri.com/jobs-in-meghalaya',
    'https://www.naukri.com/jobs-in-mizoram',
    'https://www.naukri.com/jobs-in-nagaland',
    'https://www.naukri.com/jobs-in-orissa',
    'https://www.naukri.com/jobs-in-punjab',
    'https://www.naukri.com/jobs-in-rajasthan',
    'https://www.naukri.com/jobs-in-sikkim',
    'https://www.naukri.com/jobs-in-tamil-nadu',
    'https://www.naukri.com/jobs-in-telangana',
    'https://www.naukri.com/jobs-in-tripura',
    'javascript:;' # Union territories
    'https://www.naukri.com/jobs-in-uttar-pradesh',
    'https://www.naukri.com/jobs-in-uttarakhand',
    'https://www.naukri.com/jobs-in-west-bengal'
])


NUMBERFIND = re.compile('[0-9]+')
TZ = pytz.timezone('Asia/Kolkata')

def process_link(link):
    if link in EXCEPTIONS:
        return None
    else:
        return link


def extract_number(s):
    m = NUMBERFIND.search(s)
    if m:
        return NUMBERFIND.search(s).group(0)
    else:
        return s


class NaukriSpider(CrawlSpider):
    name = 'Naukri'
    allowed_domains = ['naukri.com']
    start_urls = ['https://www.naukri.com/jobs-by-location']
    rules = (
        Rule(LinkExtractor(allow=(), 
                            restrict_xpaths=('//div[@class="colCount_four browseLoc"]',), 
                            process_value = process_link), 
            callback="parse"),
        )

    def __init__(self, jobcountfile = '', debug = False, *a, **kw):
        super(NaukriSpider, self).__init__(*a, **kw)
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(CHROMEDRIVER_PATH,chrome_options=options)

        self.debug = debug
        self.jobcountfile = jobcountfile

        # Initialize job count file
        if self.jobcountfile:        
            with open(self.jobcountfile, 'w', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(['scrapetime', 'location', 'url', 'count'])

    def __del__(self, *a, **kw):
        if hasattr(self, 'driver'):
            self.driver.quit()
        super().__del__(*a, **kw)

    def _append_jobcount(self, response):
        with open(self.jobcountfile, 'a', newline = '') as f:
            writer = csv.writer(f)
            jcelement = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sortAndH1Cont > span")))
            count = jcelement.text.split('of ')[1]
            locelement = WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sortAndH1Cont > h1")))
            location = locelement.text.split('In ')[1]
            line = [
                datetime.datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S"),
                location,
                response.url,
                count
            ]
            writer.writerow(line)
    
    def parse(self, response):
        self.driver.get(response.url)

        # check if there is some number in the URL
        m = re.search(r'\d+$', response.url)

        if not m and self.jobcountfile:
            # Then first page - write job count
            self._append_jobcount(response)

        jobs = WebDriverWait(self.driver,30).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "article.jobTuple")))

        for job in jobs:
            row = {}
            row['naukri_id'] = job.get_attribute('data-job-id')
            row['title'] = job.find_element_by_css_selector('a.title').text
            row['url'] = job.find_element_by_css_selector('a.title').get_property('href')
            row['company'] = job.find_element_by_css_selector('a.subTitle').text
            
            try:
                row['rating'] = job.find_element_by_css_selector('span.starRating').text
            except:
                row['rating'] = ''
            try:
                row['reviews'] = extract_number(job.find_element_by_css_selector('a.reviewsCount').text)
            except:
                row['reviews'] = ''
            try:
                row['experience'] = job.find_element_by_css_selector('li.experience').text
            except:
                row['experience'] = ''
            
            try:
                row['salary'] = job.find_element_by_css_selector('li.salary').text
            except:
                row['salary'] = ''
            try:
                row['location'] = job.find_element_by_css_selector('li.location').text
            except:
                row['location'] = ''
            try:
                row['job_description'] = job.find_element_by_css_selector('div.job-description').text
            except:
                row['job_description'] = ''
            
            try:
                row['tags'] = job.find_element_by_css_selector('ul.tags').text.replace('\n', ', ')
            except:
                row['tags'] = ''

            try:
                footer = job.find_element_by_css_selector('div.jobTupleFooter').text
                row['preferred'] = 1 * ('PREFERRED' in footer)
                row['hotjob'] = 1 * ('HOT JOB' in footer)
            except:
                row['preferred'] = ''
                row['hotjob'] = ''

            row['location_url'] = response.url
            row['posted_on_text'] = job.find_element_by_css_selector('i.naukicon-history + span').text
            row['timestamp'] = datetime.datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S")

            yield row

        nextdisabled = self.driver.find_element_by_css_selector('a.fright.btn-secondary.br2').get_attribute('disabled')
        if not nextdisabled:
            nextpage = self.driver.find_element_by_css_selector('a.fright.btn-secondary.br2').get_property('href')
            yield Request(nextpage, callback = self.parse)
        else:
            self.driver.quit()
            
