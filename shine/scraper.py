import os
import sys
from datetime import datetime

def modify_path():
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

modify_path()

import util.export_to_dropbox


def run_full_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'output/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'output/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    #details_local = 'output/details/shine_details_{fd}.csv'.format(fd=filedate)
    logfile_local = 'log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Shine -o "{mpl}" -a jobcountfile="{jcl}" -a logfile="{lfl}"'.format(
        mpl = mainpage_local, 
        jcl = jobcount_local, 
        lfl = logfile_local))

    # Send files to Dropbox
    mainpage_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    #details_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/details/shine_details_{fd}.csv'.format(fd=filedate)
    logfile_dropbox = '/India Labor Market Indicators/scraping/Shine/ec2/log/{fd}.log'.format(fd=filedate)
    
    util.export_to_dropbox.move_to_dropbox(mainpage_local, mainpage_dropbox)
    util.export_to_dropbox.move_to_dropbox(jobcount_local, jobcount_dropbox)
    
    # Run detail scrape
    #shine_details.run_scrape(
    #    inputfile = mainpage_local, 
    #    outputfile = details_local,
    #    logfile = logfile_local)
        
    # Move the log and details files
    #util.export_to_dropbox.move_to_dropbox(details_local, details_dropbox)
    util.export_to_dropbox.move_to_dropbox(logfile_local, logfile_dropbox)


def test_scrape():

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')

    mainpage_local = 'test/mainpage/shine_mainpage_{fd}.csv'.format(fd=filedate)
    jobcount_local = 'test/jobcount/shine_jobcount_{fd}.csv'.format(fd=filedate)
    logfile_local = 'test/log/{fd}.log'.format(fd=filedate)

    os.system('scrapy crawl Shine -o "{mainpage_local}" -a test=True -a jobcountfile="{jobcount_local}" -a logfile="{logfile_local}"'.format(mainpage_local = mainpage_local, jobcount_local = jobcount_local, logfile_local = logfile_local))
    

if __name__ == '__main__':
    # Default behavior is to run a test
    test_scrape()
    