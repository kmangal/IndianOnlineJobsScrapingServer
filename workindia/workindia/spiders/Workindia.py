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

import pytz

import requests
import re
import csv

TZ = pytz.timezone('Asia/Kolkata')

class WorkindiaSpider(scrapy.Spider):
    name = 'Workindia'
    allowed_domains = ['www.workindia.in']


    logging.getLogger().addHandler(logging.StreamHandler())
    
    def __init__(self, debug = False, jobcountfile = '', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        f = open("urls.txt")
        start_urls = ['https://www.workindia.in/jobs-in-'+url.strip().replace(" ","-").lower() for url in f.readlines()]
        f.close()
    
        self.debug = debug
        if jobcountfile:
            self.jobcountfile = jobcountfile

    def parse(self, response):
        soup = bs(response.text, 'html.parser')
        l = response.url.split("/")
        number = soup.find('h1', class_='f13 text-primary').strong.text
        number = number.strip()
        num = number.split(" ")
        number = int(num[0])
        if not any(char.isdigit() for char in response.url):
            f = open('%s.csv' % self.jobcountfile, "a")
            try:
                state = num[3]
            except Exception as e:
                state = ""
            line = [str(number), "\t", state, "\t", response.url, "\n"]
            f.writelines(line)
            f.close()
        try:
            jobs_area = soup.find_all('div', class_ = 'JobItem')
        except Exception as e:
            logging.info("No jobs in ", response.url)
        for job in jobs_area:
            try:
                title = job.find('h2', class_='text-brand').a
            except Exception as e:
                title = ""
            try:
                url = title['href']
            except Exception as e:
                url = ""
            try:
                title = title.text
            except Exception as e:
                title = ""
            try:
                views = job.find('div', class_='text-secondary f14').text
            except Exception as e:
                views = ""
            try:
                jobtype = job.find('div', class_='JobTypeDetail').text
            except Exception as e:
                jobtype = ""
            try:
                company = job.find('div', class_='CompanyDetail').text
            except Exception as e:
                company = ""
            try:
                salary = job.find('div', class_='SalaryDetail').text
            except Exception as e:
                salary = ""
            try:
                exp = job.find('div', class_='ExperienceDetail').text
            except Exception as e:
                exp = ""
            try:
                loc = job.find('div', class_='LocationDetail').text
            except Exception as e:
                loc = ""
            try:
                qual = job.find('div', class_='QualificationDetail').text
            except Exception as e:
                qual = ""
            try:
                eng = job.find('div', class_='EnglishDetail').text
            except Exception as e:
                eng = ""
            try:
                posted_on = job.find('div', class_='JobPostedOnDetail').text
            except Exception as e:
                posted_on = ""
            ct = datetime.datetime.now()
            yield {
                "title": title,
                "url": url,
                "views": views,
                "jobtype": jobtype,
                "company": company,
                "salary": salary,
                "experience": exp,
                "location": loc,
                "qualification": qual,
                "english qualification": eng,
                "posted_on": posted_on,
                "scraped_at": ct,
                "url_scraped": response.url
            }
        try:
            next_page = ""
            if not any(char.isdigit() for char in response.url):
                if number <=20:
                    pass
                else:
                    next_page = response.url + "?pg=2"
            else:
                x = l[4].split("=")[1]
                n = int(x)
                if n <= number/20:
                    next_page = l[0] + "//" + l[2] + "/" + l[3] + "/" + "?pg=" + str(n + 1)
            if next_page:
                yield Request(next_page,callback=self.parse)
        except Exception as e :
            logging.error("Exception in next_page", e)

