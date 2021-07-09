import os
from datetime import datetime
import pandas as pd
import re
import mysql.connector

FILESUFFIXRE = re.compile(r'\d{8}_\d{6}')


def read_mainpage(site, data, log):
    
    mainpagedata = read_data(data)
    
    if 'site' not in ['timesjobs', 'waahjobs']:
        mainpagelogdata = read_scrapy_log(log)
    else:
        mainpagelogdata = read_scrapelogger_mainpage(log)
        
    return {**mainpagedata, **mainpagelogdata}


def read_details(site, data, log):

    detailsdata = read_data(data)
    detailspagelogdata = read_details_log(log)
        
    return {**detailsdata, **detailspagelogdata}
    

def read_data(path):

    if not path:
        return {}

    if 'timesjobs' in path:
        site = 'timesjobs'
    elif 'monster' in path:
        site = 'monster'
    elif 'shine' in path:
        site = 'shine'
    elif 'teamlease' in path:
        site = 'teamlease'
    

    m = FILESUFFIXRE.search(path)
    
    if m:
        filesuffix = m.group()
    else:
        filesuffix = None
    
    df = pd.read_csv(path)
    
    N = df.shape[0]
    
    if N == 0:
        return {
        'nrows' : N,
        'filesuffix' : filesuffix,
        'unique_links' : 0,
        'fractionblank' : None,
        'start' : None,
        'end' : None
        } 
    
    if site == "timesjobs":
        unique_links = df['link'].unique().size
    else:
        unique_links = df['url'].unique().size
    
    if site == "timesjobs":
        time = pd.to_datetime(df['scrapetime'], format = "%d/%m/%Y %H:%M:%S")
    elif site == "shine":
        time = pd.to_datetime(df['scraped_at'], format = "%d/%m/%Y %H:%M:%S")
    else:
        time = pd.to_datetime(df['scraped_on'], format = "%d/%m/%Y %H:%M:%S")

    start = min(time)
    end = max(time)

    fractionblank = (df.values == '').sum() / (df.shape[0] * df.shape[1])

    return {
        'nrows' : N,
        'filesuffix' : filesuffix,
        'unique_links' : unique_links,
        'fractionblank' : fractionblank,
        'start' : start,
        'end' : end
        } 


def read_details_log(logfile):
   # Assumes a scrapelogger format
    
    if not logfile:
        return {}
        
    already_scraped = 0
    status0 = 0
    status1 = 0
    success = False
    retries = 0
    
    with open(logfile, 'r') as f:
    
        for line in f:
            if 'Log finished at' in line:
                success = True
            
            if 'STATUS:1' in line:
                status1 += 1
            
            if 'STATUS:0' in line:
                status0 += 1
            
            if 'Already Scraped' in line: 
                already_scraped += 1
            
            if 'Taking a break for' in line:
                retries += 1
                
    return {
        'already_scraped' : already_scraped,
        'status0' : status0,
        'status1' : status1,
        'retries' : retries,
        'success' : success
    }


def read_scrapelogger_mainpage(logfile):

    success = False
    retries = 0
    
    with open(logfile, 'r') as f:
    
        for line in f:
            if 'Log finished at' in line:
                success = True
                
            if 'Taking a break for' in line:
                retries += 1
        
    return {
        'retries' : retries,
        'success' : success
    }

def read_scrapy_log(logfile):

    error = False
    retries = 0
    spiderclose = False
    
    with open(logfile, 'r') as f:
        for line in f:        
            if 'ERROR' in line:
                error = True
            
            if 'Retrying' in line:
                retries += 1
            
            if 'Spider closed' in line:
                spiderclose = True
                
    success = spiderclose and not error
                
    return {
        'success' : success,
        'retries' : retries
    }


def update_dashboard_mainpage(site, page, log):
    # use the local version of all of these files
    
    data = read_mainpage(site, page, log)
    
    if not data:
        raise Exception("Data not parsed correctly")
        
    DB = mysql.connector.connect(
       host="india-labor.citktbvrkzg6.ap-south-1.rds.amazonaws.com",
       user="admin",
       password="b9PR]37DsB",
       database = 'dashboard'
    )
    
    cursor = DB.cursor()
    sql = "INSERT INTO mainpage_test (site, filesuffix, datastart, dataend, nrows, uniquelinks, fractionblank, retries, success) VALUES ('{}', '{}', '{}', '{}', {}, {}, {}, {}, {})".format(
        site,
        data['filesuffix'],
        data['start'].strftime('%Y-%m-%d %H:%M:%S'),
        data['end'].strftime('%Y-%m-%d %H:%M:%S'),
        data['nrows'],
        data['unique_links'],
        data['fractionblank'],
        data['retries'],
        data['success'])
    
    cursor.execute(sql)
    cursor.close()
    DB.commit()
    
    DB.close()
    
def update_dashboard_details(site, page, log):
    # use the local version of all of these files
    
    data = read_details(site, page, log)
    
    if not data:
        raise Exception("Data not parsed correctly")
        
    DB = mysql.connector.connect(
       host="india-labor.citktbvrkzg6.ap-south-1.rds.amazonaws.com",
       user="admin",
       password="b9PR]37DsB",
       database = 'dashboard'
    )
    
    cursor = DB.cursor()
    sql = "INSERT INTO details_test (site, filesuffix, datastart, dataend, nrows, uniquelinks, fractionblank, status0, status1, retries, success) VALUES ('{}', '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {})".format(
        site,
        data['filesuffix'],
        data['start'].strftime('%Y-%m-%d %H:%M:%S'),
        data['end'].strftime('%Y-%m-%d %H:%M:%S'),
        data['nrows'],
        data['unique_links'],
        data['fractionblank'],
        data['status0'],
        data['status1'],
        data['retries'],
        data['success'])
    
    cursor.execute(sql)
    cursor.close()
    DB.commit()
    
    DB.close()
    
if __name__ == '__main__':
    pass
    
    #DROPBOX = os.path.join(os.path.expanduser('~'), 'Dropbox', 'India Labor Market Indicators')
    
    #update_mainpage_database('monster', 
    #    mainpage = os.path.join(DROPBOX, 'scraping', 'Monster', 'ec2', 'mainpage', 'monster_mainpage_20210705_053308.csv'),
    #    mainpagelog = os.path.join(DROPBOX, 'scraping', 'Monster', 'ec2', 'log', '20210705_053308.log'))

    #read_scrapy_log(
    #    os.path.join(
    #        os.path.expanduser('~'), 'jobs_scraping', 'teamlease', 'test', 'log', '20210707_163236.log'
    #        )
    #    )