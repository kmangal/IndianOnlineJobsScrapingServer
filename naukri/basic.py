
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from datetime import datetime
import pytz

import re

###############################################
# Constants

TZ = pytz.timezone('Asia/Kolkata')
NUMBERFIND = re.compile('[0-9]+')

CHROMEDRIVER_PATH = '/home/ec2-user/naukri/chromedriver'

###############################################
# Functions

def extract_number(s):
    m = NUMBERFIND.search(s)
    if m:
        return NUMBERFIND.search(s).group(0)
    else:
        return s

###############################################
# Main

options = Options()
options.headless = True
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
driver.get('https://www.naukri.com/jobs-in-mumbai')

jobs = driver.find_elements_by_css_selector("article.jobTuple")

jobcount = driver.find_element_by_css_selector('div.sortAndH1Cont > span').text.split('of ')[1]
print("There are {} jobs".format(jobcount))

job = jobs[0]
data = {}
data['naukri_id'] = job.get_attribute('data-job-id')
data['title'] = job.find_element_by_css_selector('a.title').text
data['url'] = job.find_element_by_css_selector('a.title').get_property('href')
data['company'] = job.find_element_by_css_selector('a.subTitle').text
data['rating'] = job.find_element_by_css_selector('span.starRating').text
data['reviews'] = extract_number(job.find_element_by_css_selector('a.reviewsCount').text)
data['experience'] = job.find_element_by_css_selector('li.experience').text
data['salary'] = job.find_element_by_css_selector('li.salary').text
data['location'] = job.find_element_by_css_selector('li.location').text
data['job_description'] = job.find_element_by_css_selector('div.job-description').text
data['tags'] = job.find_element_by_css_selector('ul.tags').text.replace('\n', ', ')

footer = job.find_element_by_css_selector('div.jobTupleFooter').text
data['preferred'] = 1 * ('PREFERRED' in footer)
data['hotjob'] = 1 * ('HOT JOB' in footer)
data['posted_on_text'] = job.find_element_by_css_selector('i.naukicon-history + span').text
data['timestamp'] = datetime.now().astimezone(TZ).strftime("%d/%m/%Y %H:%M:%S")

driver.close()

