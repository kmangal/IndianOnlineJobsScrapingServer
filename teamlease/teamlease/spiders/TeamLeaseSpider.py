import scrapy
from bs4 import BeautifulSoup as bs
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
from scrapy import signals

import datetime
import pytz
import logging
import re
import csv
import requests

TZ = pytz.timezone('Asia/Kolkata')

class TeamLeaseSpider(scrapy.Spider):

    name = 'Teamlease'
    allowed_domains = ['teamlease.com']
    start_urls = ['http://www.teamlease.com/jobs/']
    handle_httpstatus_list = [404, 500, 502]
 
    def __init__(self, debug = False, jobcountfile = '', logfile = '', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug
        self.failed_urls = []
        
        if not logfile:
            raise Exception("Log file path missing")
        else:
            logging.getLogger().addHandler(logging.FileHandler(logfile))

        if jobcountfile:
            self._getjobcount(jobcountfile)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TeamLeaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.handle_spider_closed, signals.spider_closed)
        return spider

    def handle_spider_closed(self, reason):
        self.crawler.stats.set_value('failed_urls', ', '.join(self.failed_urls))

    def process_exception(self, response, exception, spider):
        ex_class = "%s.%s" % (exception.__class__.__module__, exception.__class__.__name__)
        self.crawler.stats.inc_value('downloader/exception_count', spider=spider)
        self.crawler.stats.inc_value('downloader/exception_type_count/%s' % ex_class, spider=spider)


    def _getjobcount(self, jobcountfile):
        
        success = False

        page = requests.get('http://www.teamlease.com/jobs/')
        soup = bs(page.text, 'html.parser')
        countelement = soup.find('div', class_ = "total_jobs")
        
        if countelement:
            m = re.search('[0-9]+', countelement.text)
            if m:
                totalcount = m.group(0)
                success = True
        
        if success:
            f = open(jobcountfile, 'w', newline = '')
            writer = csv.DictWriter(f, fieldnames = ['scrapetime', 'url', 'count'])
            writer.writeheader()
            writer.writerow({
                'scrapetime' : datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                'url' : 'http://www.teamlease.com/jobs/',
                'count' : int(totalcount)
            })
            f.close()
            logging.info("Job count file saved to {}".format(jobcountfile))
        else:
            logging.error("Job count not found")


    def parse(self, response):
        # urls = response.xpath('//div[@class="job-card"]/@job_display_url').getall()
        # print(urls)

        offset_split = response.url.split('?offset=')
        if len(offset_split) == 1:
            offset_value = 0
        else:
            offset_value = int(offset_split[1])

        if response.status in [404, 500, 502]:
            self.crawler.stats.inc_value('failed_url_count')
            self.failed_urls.append(response.url)
            yield Request('https://www.teamlease.com/jobs?offset={}'.format(offset_value), callback = self.parse)
            return None

        soup  = bs(response.text, 'html.parser')
        # print(soup)
        jobs_area =  soup.find('div', id="stickymiddleblock")
        # print(jobs_area)
        jobs = jobs_area.find_all('div', class_='main-job-div')
        # print(jobs)
        for job in jobs:
            try:
                job_info = job.find('div', class_="job-card")
            except Exception as e:
                job_info = ""
            try:
                job_id = job["job_id"]
            except Exception as e:
                job_id = ""
            try:
                url = job_info["job_display_url"]
            except Exception as e:
                url = ""
            try:
                title = job_info.find('b', class_="job_title").text.strip()
            except Exception as e:
                title = ""
            try:
                company = job_info.find('div', class_="company-name").text.strip()
            except Exception as e:
                company = ""
            try:
                exp = job_info.find('span', class_="experience").text
            except Exception as e:
                exp = ""
            try:
                loc_info = job_info.find('a', alt="location")
                loc = loc_info.span.text.strip()
                loc_url = loc_info['href']
            except Exception as e:
                loc_url = ""
            try:
                sal = job_info.find('div', class_="salary-section")
                salary = ""
                lsal = sal.find('span').nextSibling
                usal = lsal.nextSibling
                lsal = lsal.text.strip()
                usal = usal.text.strip()
            except Exception as e:
                lsal = ""
                usal = ""
            salary = lsal + usal
            try:
                desc = job_info.find('span', class_="job-desc").nextSibling
                desc = desc.text.strip()
            except Exception as e:
                desc = ""
            try:
                tag = job_info.find('div', class_="premium-section").span.text.strip()
            except Exception as e:
                tag = ""
            try:
                posted = job.find('div', class_="date-of-posting").span
                posted_timestamp = int(posted["posted-on"].split()[0])
                posted_on = posted.text.strip()
            except Exception as e:
                posted_on = ""
                posted_timestamp = ""
            
            yield {
                "job_id": job_id,
                "url": url,
                "title": title,
                "company": company,
                "experience": exp,
                "location": loc,
                "location_url": loc_url,
                "salary": salary,
                "job description": desc,
                "tag": tag,
                "posted_on_text": posted_on,
                "posted_on_timestamp": datetime.datetime.fromtimestamp(posted_timestamp).strftime("%d/%m/%Y %H:%M:%S"),
                "scraped_on": datetime.datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S"),
                "url-scraped": response.url
            }

        
        if self.debug:
            raise CloseSpider("Debug Mode")

        if self._is_last_page(soup):
            raise CloseSpider("Reached last page")

        nextpagelink = soup.select("li#dataTables-example_next > a")[0]
        offset = nextpagelink['href']

        yield Request('https://www.teamlease.com/jobs{}'.format(offset), callback = self.parse)

    def _is_last_page(self, soup):
            
        nextpage = soup.select("li#dataTables-example_next")[0]
        return ('disabled' in nextpage['class'])


