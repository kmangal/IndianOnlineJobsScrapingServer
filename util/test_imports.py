import os
import importlib

import sys
sys.path.append('../')

jobs_scraping_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def is_exception(modulepath):
    ''' Ignore certain files and folders'''
    
    if modulepath == "util.test_imports":
        return True
    elif 'naukri' in modulepath:
        return True
    elif 'test' in modulepath:
        return True
    else:
        return False

for root, dirs, files in os.walk(jobs_scraping_folder, topdown=False):
    
    for name in files:
        if name.endswith('.py') and name != "__init__.py":
        
            if os.name == 'nt':
                folder = root.split('jobs_scraping\\')[1]
                importpath = folder.replace('\\', '.')
            else:
                folder = root.split('jobs_scraping/')[1]
                importpath = folder.replace('/', '.')
                
            scriptname = name.split('.py')[0]
            modulepath = importpath + '.' + scriptname
            
            if not is_exception(modulepath):
                print(modulepath)
                importlib.import_module(modulepath)
