import os
import sys
import glob


if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        raise Exception("syntax: seelog.py [site]")
    
    site = sys.argv[1]
    if site not in ['shine', 'monster', 'timesjobs', 'teamlease', 'waahjobs']:
        raise Exception("site not correctly specified")
        
    userdir = os.path.expanduser('~')
    logdir = os.path.join(userdir, 'jobs_scraping', site, 'log')

    logs = glob.glob(logdir + '/*.log')
    if logs:
        latest_log = max(logs, key=os.path.getctime)
        print('Latest log', latest_log)
        print('--------------------------------------')
        os.system('tail -n 10 {}'.format(latest_log))
    else:
        print("No logs found")