import scrapy
from bs4 import BeautifulSoup as bs
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider

import datetime

import logging
import csv
import re

import pytz
TZ = pytz.timezone('Asia/Kolkata')

# 3 india restrictions are because in they show up in the top locations
# in aggregate form and are repeated in finer subunits in the state section

EXCLUSIONS = set([
    'https://www.monsterindia.com/search/jobs-in-bangalore',
    'https://www.monsterindia.com/search/jobs-in-mumbai',
    'https://www.monsterindia.com/search/jobs-in-delhi-ncr',
    'https://www.monsterindia.com/search/jobs-in-australia',
    'https://www.monsterindia.com/search/jobs-in-germany',
    'https://www.monsterindia.com/search/jobs-in-kuwait',
    'https://www.monsterindia.com/search/jobs-in-qatar',
    'https://www.monsterindia.com/search/jobs-in-south-korea',
    'https://www.monsterindia.com/search/jobs-in-canada',
    'https://www.monsterindia.com/search/jobs-in-hong-kong',
    'https://www.monsterindia.com/search/jobs-in-malaysia',
    'https://www.monsterindia.com/search/jobs-in-saudi-arabia',
    'https://www.monsterindia.com/search/jobs-in-thailand',
    'https://www.monsterindia.com/search/jobs-in-dubai',
    'https://www.monsterindia.com/search/jobs-in-japan',
    'https://www.monsterindia.com/search/jobs-in-mauritius',
    'https://www.monsterindia.com/search/jobs-in-singapore',
    'https://www.monsterindia.com/search/jobs-in-uae',
    'https://www.monsterindia.com/search/jobs-in-france',
    'https://www.monsterindia.com/search/jobs-in-jordan',
    'https://www.monsterindia.com/search/jobs-in-oman',
    'https://www.monsterindia.com/search/jobs-in-south-africa',
    'https://www.monsterindia.com/search/jobs-in-usa'
])

# For state level
#def clean_link(value):
    # Some of the links on their own site are bad, so we need to manually fix them
#    if value == 'https://www.monsterindia.com/search/jobs-in-tamilnadu':
#        return 'https://www.monsterindia.com/search/jobs-in-tamil-nadu'
#    elif value == 'https://www.monsterindia.com/search/jobs-in-chattisgarh':
#        return 'https://www.monsterindia.com/search/jobs-in-chhattisgarh'
#    elif value == 'https://www.monsterindia.com/search/jobs-in-jharkand':
#        return 'https://www.monsterindia.com/search/jobs-in-jharkhand'
#    else:
#        return value

def process_links(link):
    if link in EXCLUSIONS:
        return None
    else:
        return link 

class MonsterSpider(CrawlSpider):

    name = 'Monster'
    allowed_domains = ['monsterindia.com']
    start_urls = ['https://www.monsterindia.com/search/jobs-by-location']
    rules = (
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@class="ar-link"]',), process_value = process_links), callback="parse"),
        )
        
    # To also print to console
    logging.getLogger().addHandler(logging.StreamHandler())
    
    def __init__(self, jobcountfile = '', test = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.test = test
        self.jobcountfile = jobcountfile

        self.pagecounter = 0

        # Initialize job count file
        if jobcountfile:        
            with open(self.jobcountfile, 'w', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow(['scrapetime', 'location', 'url', 'count'])

    def _append_jobcount(self, response):
        with open(self.jobcountfile, 'a', newline = '') as f:
            writer = csv.writer(f)
            count = response.xpath('//strong[@class="fs-24 normal ffm-arial"]/text()').get()
            location = response.xpath('//h1[@class="fs-24 srp-seo-data capitalize ib normal"]/text()').get()
            location = location.strip()
            location = location.split(" ")[2]
            line = [
                datetime.datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S"),
                location,
                response.url,
                count
            ]
            writer.writerow(line)

    def parse(self, response):

        soup  = bs(response.text, 'html.parser')
        noresult = soup.select('no-result')
        if noresult:
            return

        # Take out the searchId part - check if the stem ends with a number to determine if it's the first page
        urlstem = response.url.split('?')[0]
        m = re.search(r'\d+$', urlstem)

        if not m and self.jobcountfile:
            # Then first page - write job count
            self._append_jobcount(response)

        jobs_area = soup.find('div', id = 'srp-jobList')
        jobs = jobs_area.find_all('div', class_='card-panel apply-panel job-apply-card')
        for job in jobs:
            up_area = job.find('div', class_='job-tittle')
            title_area = up_area.find('h3', class_='medium')
            title = title_area.a.text.strip()
            url = title_area.a['href']
            try:
                company = up_area.find('span', class_='company-name').a.text.strip()
            except Exception as e:
                company = ""
            try:
                loc = up_area.find_all('span', class_='loc')
                locs = ""
                l = loc[0].find_all('small')
                for x in l:
                    locs = locs + x.text.strip() + ','
            except Exception as e:
                locs = ""
            exp = loc[1].small.text.strip()
            sal = loc[2].small.text.strip()
            try:
                desc = job.find('p', class_='job-descrip').text.strip()
            except Exception as e:
                desc = ""
            try:
                skills_area = job.find('p', class_='descrip-skills')
                skills = skills_area.find_all('label', class_='grey-link')
                skill = ""
                for s in skills:
                    skill = skill + s.a.text.strip() + ","
            except Exception as e:
                skill = ""
            try:
                posted_at = soup.find('span', class_='posted').text.strip()
            except Exception as e:
                posted_at = ""

            yield {
                'title': title,
                'url': url,
                'company': company,
                'location': locs,
                'experience': exp,
                'salary': sal,
                'description': desc,
                'skills': skill,
                'posted_at': posted_at,
                'scraped_on': datetime.datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S"),
                'url_scraped': response.url
            }

        self.pagecounter += 1

        if self.test and self.pagecounter > 10:
            raise CloseSpider("Debug Mode - Limited scrape")
    
        buttons = soup.select("div.srp-navigation > a")
        links = dict()
        for elem in buttons:
            links[elem.text.strip()] = elem['href']

        if 'Next' in links:
            yield Request(links['Next'], callback = self.parse)

