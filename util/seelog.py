import os
import sys
import glob

import argparse


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("site")
    parser.add_argument("-sub", required = False)

    parser.add_argument("-n", help="number of lines to display", default = 10, type = int, required = False)
    args = parser.parse_args()

    if args.site not in ['shine', 'monster', 'timesjobs', 'teamlease', 'waahjobs']:
        raise Exception("site not correctly specified")
    
    if args.subfolder and args.subfolder not in ['mainpage', 'details']:
        raise Exception('subfolder not correctly specified')
        
    userdir = os.path.expanduser('~')
    if not args.subfolder:
        logdir = os.path.join(userdir, 'jobs_scraping', args.site, 'log')
    else:
        logdir = os.path.join(userdir, 'jobs_scraping', args.site, args.subfolder, 'log')
    
    logs = glob.glob(logdir + '/*.log')
    if logs:
        latest_log = max(logs, key=os.path.getctime)
        print('Latest log', latest_log)
        print('--------------------------------------')
        os.system('tail -n {lines} {log}'.format(lines = args.n, log = latest_log))
    else:
        print("No logs found")