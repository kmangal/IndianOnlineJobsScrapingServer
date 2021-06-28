import logging
import sys
import datetime

class ScrapeLogger:
    
    def __init__(self, name, path, level = logging.DEBUG):
         
        self.starttime = datetime.datetime.now()

        self.log = logging.getLogger(name)
        self.log.setLevel(level)
            
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p %Z')
    
        log_filehandler = logging.FileHandler(path)    
        log_filehandler.setFormatter(log_format)
        self.log.addHandler(log_filehandler)
        
        log_streamhandler = logging.StreamHandler()
        log_streamhandler.setFormatter(log_format)
        self.log.addHandler(log_streamhandler)

        # Include unhandled exceptions in the log file
        self.log.info('Log running at {}'.format(self.starttime.strftime('%m/%d/%Y %I:%M:%S %p %Z')))
        sys.excepthook = self.handle_exception


    def finalize(self):
        self.endtime = datetime.datetime.now()
        self.log.info('Log finished at {}'.format(self.endtime.strftime('%m/%d/%Y %I:%M:%S %p %Z')))
    

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    

