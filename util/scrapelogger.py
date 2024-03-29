import logging
import logging.handlers
import sys
import datetime

MSGFORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATEFORMAT = '%m/%d/%Y %I:%M:%S %p %Z'
    
class BaseLogger:
    
    def __init__(self, name, path, level = logging.DEBUG):
         
        self.starttime = datetime.datetime.now()

        self.log = logging.getLogger(name)
        self.log.setLevel(level)
            
        self.log_format = logging.Formatter(MSGFORMAT, datefmt= DATEFORMAT)
        
        log_streamhandler = logging.StreamHandler()
        log_streamhandler.setFormatter(self.log_format)
        self.log.addHandler(log_streamhandler)

    def start(self):    
        # Include unhandled exceptions in the log file
        sys.excepthook = self.handle_exception
        self.log.info('Log running at {}'.format(self.starttime.strftime('%m/%d/%Y %I:%M:%S %p %Z')))

    def finalize(self):
        self.endtime = datetime.datetime.now()
        self.log.info('Log finished at {}'.format(self.endtime.strftime('%m/%d/%Y %I:%M:%S %p %Z')))
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


class ScrapeLogger(BaseLogger):
    
    def __init__(self, name, path, level = logging.DEBUG):
    
        super().__init__(name, path, level)
            
        log_filehandler = logging.FileHandler(path)    
        log_filehandler.setFormatter(self.log_format)
        self.log.addHandler(log_filehandler)
        
        self.start()

    
class RotatingLogger(BaseLogger):
    
    def __init__(self, name, path, level = logging.DEBUG):
         
        super().__init__(name, path, level)

        log_filehandler = logging.handlers.TimedRotatingFileHandler(path, when = 'd', interval = 7)    
        log_filehandler.setFormatter(self.log_format)
        self.log.addHandler(log_filehandler)
        
        self.start()
        

import scrapy.logformatter

class ScrapyLogFormatter(scrapy.logformatter.LogFormatter):
    def scraped(self, item, response, spider):
        return (
            super().scraped(item, response, spider)
            if spider.settings.getbool("LOG_SCRAPED_ITEMS")
            else None
        )