import logging
import io
import sys
import datetime

class ScrapeLogger:
    
    def __init__(self, name, level = logging.DEBUG):
         
        self.starttime = datetime.datetime.now()

        self.log = logging.getLogger(name)
        self.log.setLevel(level)
            
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %Z')
    
        log_consolehandle = logging.StreamHandler(sys.stdout)    
        log_consolehandle.setFormatter(log_format)
        self.log.addHandler(log_consolehandle)

        self.log.info('Log running at {}'.format(self.starttime.strftime('%m/%d/%Y %I:%M:%S %p %Z')))

    def finalize(self):
        self.endtime = datetime.datetime.now()
        self.log.info('Log finished at {}'.format(self.endtime.strftime('%m/%d/%Y %I:%M:%S %p %Z')))
    
