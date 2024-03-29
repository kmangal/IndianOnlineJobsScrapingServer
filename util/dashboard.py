import os
from datetime import datetime
import pandas as pd
import numpy as np
import re
import mysql.connector

FILESUFFIXRE = re.compile(r'\d{8}_\d{6}')

def get_file_suffix(path):
    m = FILESUFFIXRE.search(path)
    
    if m:
        filesuffix = m.group()
    else:
        filesuffix = "NULL"

    return filesuffix

def read_mainpage(site, data, log):
    
    mainpagedata = read_data(data)
    
    if site not in ['timesjobs', 'waahjobs']:
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

    df = pd.read_csv(path)
    
    N = df.shape[0]
    
    if N == 0:
        return {
        'nrows' : N,
        'unique_links' : 0,
        'fractionblank' : "NULL",
        'start' :"NULL",
        'end' : "NULL"
        } 
    
    if 'link' in df.columns:
        unique_links = df['link'].unique().size
    elif 'url' in df.columns:
        unique_links = df['url'].unique().size
    else:
        unique_links = "NULL"
    
    if 'scrapetime' in df.columns:
        time = pd.to_datetime(df.loc[df['scrapetime'] != '', 'scrapetime'], format = "%d/%m/%Y %H:%M:%S")
    elif 'scraped_at' in df.columns:
        time = pd.to_datetime(df.loc[df['scraped_at'] != '', 'scraped_at'], format = "%d/%m/%Y %H:%M:%S")
    elif 'scraped_on' in df.columns:
        time = pd.to_datetime(df.loc[df['scraped_on'] != '', 'scraped_on'], format = "%d/%m/%Y %H:%M:%S")
    else:
        time = np.array([])
    
    if time.size > 0:    
        start = min(time)
        end = max(time)
    else:
        start = "NULL"
        end = "NULL"
        
    fractionblank = (np.sum(df.isnull().sum()) + (df.values == 'MISSING').sum()) / (df.shape[0] * df.shape[1])

    return {
        'nrows' : N,
        'unique_links' : unique_links,
        'fractionblank' : fractionblank,
        'start' : start,
        'end' : end
        } 


def read_details_log(logfile):
   # Assumes a scrapelogger format
    
    if logfile is None or not os.path.isfile(logfile) or os.path.getsize(logfile) == 0:
        return {'already_scraped' : "NULL", 'status0' : "NULL", 'status1' : "NULL", 'retries' : "NULL", 'success': "NULL", 'logmissing' : True}
        
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
        'success' : success,
        'logmissing' : False
    }


def read_scrapelogger_mainpage(logfile):

    if logfile is None or not os.path.isfile(logfile) or os.path.getsize(logfile) == 0:
        return {'retries' : "NULL", 'success': "NULL", 'logmissing' : True}
        
    success = False
    retries = 0
    
    with open(logfile, 'r') as f:
    
        for line in f:
            if 'Log finished at' in line:
                success = True
                
            if 'Taking a break for' in line or 'Connection reset' in line:
                retries += 1
        
    return {
        'retries' : retries,
        'success' : success,
        'logmissing' : False
    }

def read_scrapy_log(logfile):

    if logfile is None or not os.path.isfile(logfile) or os.path.getsize(logfile) == 0:
        return {'retries' : "NULL", 'success': "NULL", 'logmissing' : True}
    
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
        'retries' : retries,
        'logmissing' : False
    }


def record_exists(DB, table, site, filesuffix):
    cursor = DB.cursor()
    cursor.execute("SELECT 1 FROM {} where site = '{}' and filesuffix = '{}'".format(table, site, filesuffix))
    result = cursor.fetchall()
    cursor.close()

    if result:
        return True
    else:
        return False

def update_dashboard_mainpage(site, page, log, test = False, overwrite = False):
    # use the local version of all of these files

    DB = mysql.connector.connect(
       host="india-labor.citktbvrkzg6.ap-south-1.rds.amazonaws.com",
       user="admin",
       password="b9PR]37DsB",
       database = 'dashboard'
    )

    filesuffix = get_file_suffix(page)

    if test:
        table = 'mainpage_test'
    else:
        table = 'mainpage'
        
    if not overwrite:
        if record_exists(DB, table, site, filesuffix):
            DB.close()
            return

    data = read_mainpage(site, page, log)
    
    if not data:
        raise Exception("Data not parsed correctly")
    
    if test:
        print(data)
                    
    cursor = DB.cursor()
    sql = '''INSERT INTO {} 
    (site, filesuffix, datastart, dataend, nrows, uniquelinks, fractionblank, retries, success, logmissing) 
    VALUES ('{}', '{}', '{}', '{}', {}, {}, {}, {}, {}, {})
    ON DUPLICATE KEY UPDATE
    `datastart` = VALUES(`datastart`),
    `dataend` = VALUES(`dataend`),
    `nrows` = VALUES(`nrows`),
    `uniquelinks` = VALUES(`uniquelinks`),
    `fractionblank` = VALUES(`fractionblank`),
    `retries` = VALUES(`retries`),
    `success` = VALUES(`success`),
    `logmissing` = VALUES(`logmissing`)'''.format(
        table,
        site,
        filesuffix,
        data['start'],
        data['end'],
        data['nrows'],
        data['unique_links'],
        data['fractionblank'],
        data['retries'],
        data['success'],
        data['logmissing'])
    
    cursor.execute(sql)
    cursor.close()
    DB.commit()
    
    DB.close()
    
def update_dashboard_details(site, page, log, test = False, overwrite= False):
    # use the local version of all of these files

    DB = mysql.connector.connect(
       host="india-labor.citktbvrkzg6.ap-south-1.rds.amazonaws.com",
       user="admin",
       password="b9PR]37DsB",
       database = 'dashboard'
    )
        
    filesuffix = get_file_suffix(page)

    if test:
        table = 'details_test'
    else:
        table = 'details'
        
    if not overwrite:
        if record_exists(DB, table, site, filesuffix):
            DB.close()
            return
    
    data = read_details(site, page, log)
    
    if not data:
        raise Exception("Data not parsed correctly")
    
    if test:
        print(data)
            
    cursor = DB.cursor()
    sql = '''INSERT INTO {} 
            (site, filesuffix, datastart, dataend, nrows, uniquelinks, fractionblank, alreadyscraped, status0, status1, retries, success, logmissing) 
            VALUES ('{}', '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {})
            ON DUPLICATE KEY UPDATE
            `datastart` = VALUES(`datastart`),
            `dataend` = VALUES(`dataend`),
            `nrows` = VALUES(`nrows`),
            `uniquelinks` = VALUES(`uniquelinks`),
            `fractionblank` = VALUES(`fractionblank`),
            `alreadyscraped` = VALUES(`alreadyscraped`),
            `status0` = VALUES(`status0`),
            `status1` = VALUES(`status1`),
            `retries` = VALUES(`retries`),
            `success` = VALUES(`success`),
            `logmissing` = VALUES(`logmissing`)'''.format(
        table,
        site,
        filesuffix,
        data['start'],
        data['end'],
        data['nrows'],
        data['unique_links'],
        data['fractionblank'],
        data['already_scraped'],
        data['status0'],
        data['status1'],
        data['retries'],
        data['success'],
        data['logmissing'])
    
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