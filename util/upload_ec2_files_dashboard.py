# -*- coding: utf-8 -*-

#THIS FILE DOESN'T RUN ON THE SERVER - ONLY ON THE LOCAL WHERE DROPBOX IS STORED

import dashboard
import os
import glob

import re
FILESUFFIXRE = re.compile(r'\d{8}_\d{6}')

DROPBOX = os.path.join(os.path.expanduser("~"), "Dropbox", "India Labor Market Indicators", "scraping")

LOCAL_TO_DROPBOX = {
    'timesjobs' : 'TimesJobs',
    'teamlease' : 'TeamLease',
    'shine' : 'Shine',
    'waahjobs' : 'Waahjobs',
    'monster' : 'Monster'
   }


def upload_details(site):
    
    sitefolder = os.path.join(DROPBOX, LOCAL_TO_DROPBOX[site])

    detailsfolder = os.path.join(sitefolder, 'ec2', 'output', 'details', "*.csv")
    for detailsfile in glob.glob(detailsfolder):
        print(detailsfile)
        m = FILESUFFIXRE.search(detailsfile)
        if m:
            logfile = os.path.join(sitefolder, 'ec2', 'log', 'details', '{}.log'.format(m.group()))
        else:
            logfile = None
            
        dashboard.update_dashboard_details(site, detailsfile, logfile)

def upload_mainpage(site):
    
    sitefolder = os.path.join(DROPBOX, LOCAL_TO_DROPBOX[site])
    mainpagefolder = os.path.join(sitefolder, 'ec2', 'output', 'mainpage', "*.csv")
    for mainfile in glob.glob(mainpagefolder):
        print(mainfile)
        m = FILESUFFIXRE.search(mainfile)
        if m:
            logfile = os.path.join(sitefolder, 'ec2', 'log', 'mainpage', '{}.log'.format(m.group()))
        else:
            logfile = None
            
        dashboard.update_dashboard_mainpage(site, mainfile, logfile)
        

if __name__ == '__main__':
    for site in ['teamlease', 'shine', 'monster', 'timesjobs']:
        print(site)
        upload_mainpage(site)
        upload_details(site)
