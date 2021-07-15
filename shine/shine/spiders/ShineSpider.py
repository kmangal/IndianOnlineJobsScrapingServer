import scrapy
from bs4 import BeautifulSoup as bs
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime
from scrapy.crawler import CrawlerProcess

from scrapy.exceptions import CloseSpider

import logging
import os


import requests
import re
import csv
import sys


class ShineSpider(scrapy.Spider):

    name = 'Shine'
    allowed_domains = ['shine.com']
    start_urls = ['https://www.shine.com/job-search/jobs']

    def __init__(self, jobcountfile = '', test = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test = test
        
        if jobcountfile:
            self._getjobcount(jobcountfile)

        self.pagecount = 0
        
    def _getjobcount(self, jobcountfile):
        
        success = False

        page = requests.get('https://www.shine.com/job-search/jobs')
        soup = bs(page.text, 'html.parser')
        countelement = soup.find(id = "id_resultCount")
        
        if countelement:
            m = re.search('(?<=of)[ ]+[0-9]+', countelement.text)
            if m:
                totalcount = m.group(0)
                success = True
        
        if success:
            f = open(jobcountfile, 'w', newline = '')
            writer = csv.DictWriter(f, fieldnames = ['scrapetime', 'url', 'count'])
            writer.writeheader()
            writer.writerow({
                'scrapetime' : datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                'url' : 'https://www.shine.com/job-search/jobs',
                'count' : int(totalcount)
            })
            f.close()
            logging.info("Job count file saved to {}".format(jobcountfile))
        else:
            logging.error("Job count not found")

    def parse(self, response):

        soup  = bs(response.text, 'html.parser')
        jobs_area = soup.find('div', class_ = 'force-overflow base_color pl-10 pt-10 pr-10')
        
        if not jobs_area:
            # just skip for now
            self.get_next_page(soup)
            
        jobs = jobs_area.find_all('li', class_='result-display__profile')
        
        for job in jobs:
            job_id = job['id']
            premium = job.find('span', class_='icon-premium mr-5')
            if premium:
                premium = "premium"
            title = job.find('a', class_='job_title_anchor')
            url = title["href"]
            try:
                company = job.find('span', class_='result-display__profile__company-name').text.strip()
            except Exception as e:
                company = ""
            try:
                exp_loc = job.find_all('li', class_='result-display__profile__years')
            except Exception as e:
                exp_loc = ""
                
            if exp_loc:
                try:
                    exp = exp_loc[0].text.strip()
                except Exception as e:
                    exp = ""
                try:
                    loc = exp_loc[1].text.strip()
                except Exception as e:
                    loc = ""
            try:
                posted_at = job.find('li', class_='result-display__profile__date').text.strip()
            except Exception as e:
                posted_at = ""

            yield {
                "id" : job_id,
                "premium" : premium,
                "title" : title.text,
                "url" : url,
                "company": company,
                "experience": exp,
                "location": loc,
                "posted_at": posted_at,
                "scraped_at": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "url-scraped": response.url
            }
        
        self.pagecount += 1
        
        if self.test and self.pagecount > 2:
            raise CloseSpider("Test Mode")

    def get_next_page(self, soup):
        
        # Go to next page
        pagelinks = soup.select("a.submit.submit1.pagination_button.cls_pagination")
        pagelinktext = [a.text for a in pagelinks]
        if 'Next>' in pagelinktext:
            lastpagehref = pagelinks[-1]['href']
            # Shine seems to have an anti scraping measure in place where they put the wrong url in the raw html
            # (but it shows up okay on their website). Strategy: just extract the number.
            m = re.search('[0-9]+', lastpagehref)
            nextpagenumber = m.group(0)
            yield Request('https://www.shine.com/job-search/jobs-{}'.format(nextpagenumber), callback=self.parse)      
        else:
            raise CloseSpider("Reached last page")
