import requests
import json

from datetime import datetime

import csv
import os
import sys
sys.path.append('../')

import util.export_to_dropbox
from util import scrapelogger

import pathlib
WAAHJOBS_PATH = pathlib.Path(__file__).parent.resolve()

API_START_URL = 'https://www.waahjobs.com/api/v5/search/jobs/' + '?offset=0'

API_HEADERS = {
                'content-type': 'application/json',
                'Cookie': '__cfduid=dba68c5578a17f6ab098519bc8defa8521600083451'
              }


def get_data(url, headers):
    response = requests.request("GET", url, headers=headers)
    response = response.text.encode('utf8')
    response = json.loads(response)
    
    nextlink = response['meta'].get('next', '')
    rows = response['objects']
    
    return rows, nextlink


def write_rows(csvwriter, rows):

    for line in rows:
        line_out = dict((k, line[k]) for k in ('_index', '_type', '_id', '_score'))
        for key, value in line['_source'].items():
            line_out[key] = value

        csvwriter.writerow(line_out)


def run_scrape(test = False):

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    if test:
        outpath = os.path.join(WAAHJOBS_PATH, 'test', 'api', 'waahjobs_api_{fd}.csv'.format(fd = filedate))
        logpath = os.path.join(WAAHJOBS_PATH, 'test', 'log', '{fd}.log'.format(fd=filedate))
        logger = scrapelogger.ScrapeLogger('waahjobs-api', logpath)
    else:
        outpath = os.path.join(WAAHJOBS_PATH, 'output', 'api', 'waahjobs_api_{fd}.csv'.format(fd = filedate))
        logpath = os.path.join(WAAHJOBS_PATH, 'log', '{fd}.log'.format(fd=filedate))
        logger = scrapelogger.ScrapeLogger('waahjobs-api', logpath)
    
    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        rows, nextlink = get_data(API_START_URL, API_HEADERS)
        headerrow = list(rows[0].keys())
        headerrow.remove('_source')
        headerrow = headerrow + list(rows[0]['_source'].keys())
        csvwriter = csv.DictWriter(f, headerrow)
        
        csvwriter.writeheader()
        write_rows(csvwriter, rows)
        
        if test:
            raise Exception("Test")
            
        while nextlink:
            logger.log.info(nextlink)
            rows, nextlink = get_data(nextlink, API_HEADERS)
            write_rows(csvwriter, rows)
                    
    logger.finalize()
    
    if not test:
        api_dropbox = '/India Labor Market Indicators/scraping/WaahJobs/ec2/api/waahjobs_api_{fd}.csv'.format(fd=filedate)
        log_dropbox = '/India Labor Market Indicators/scraping/WaahJobs/ec2/log/{fd}.log'.format(fd=filedate)

        util.export_to_dropbox.move_to_dropbox(outpath, api_dropbox)
        util.export_to_dropbox.move_to_dropbox(logpath, log_dropbox)
           
            
if __name__ == '__main__':

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')
    run_scrape(filedate, test = True)
