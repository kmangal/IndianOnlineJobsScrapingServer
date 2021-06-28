import requests
import json

import pandas as pd
from datetime import datetime

import sys
sys.path.append('../')
import util.export_to_dropbox




API_START_URL = 'https://www.waahjobs.com/api/v5/search/jobs/' + '?offset=0'

API_HEADERS = {
                'content-type': 'application/json',
                'Cookie': '__cfduid=dba68c5578a17f6ab098519bc8defa8521600083451'
              }


def get_data(url, headers):
    response = requests.request("GET", url, headers=headers)
    response = response.text.encode('utf8')
    response = json.loads(response)
    
    nextlink = response['meta'].get('next', '')
    rows = response['objects']
    
    return rows, nextlink


'''
def write_result(data, path):
	today = date.today()
	today = today.strftime("%Y_%m_%d")
	json_path = config.OUTPUT_PATH+path+'/'+path+'_'+today+'.json'
	csv_path = config.OUTPUT_PATH+path+'/'+path+'_'+today+'.csv'
	os.makedirs(os.path.dirname(json_path), exist_ok=True)
	with open(json_path, "w") as f:
		f.write(data)
	if path == "WI_API":
		with open(json_path, encoding='utf-8-sig') as f_input:
			df = pd.read_json(f_input)
		df.to_csv(csv_path, encoding='utf-8', index=False)	
	if path == "AJ_API":
		with open(json_path) as json_file: 
			data = json.load(json_file) 
		data_file = open(csv_path, 'w')
		csv_writer = csv.writer(data_file)
		count = 0
		for emp in data:
			emp = emp["_source"]
			if count == 0: 
				header = emp.keys() 
				csv_writer.writerow(header) 
				count += 1
		  
			csv_writer.writerow(emp.values()) 
		  
		data_file.close()
'''        

#def api_call(outpath):
    
if __name__ == '__main__':

    filedate = datetime.today().strftime('%Y%m%d_%H%M%S')
    outpath = 'output/api/waahjobs_api_{fd}.csv'.format(fd = filedate)

    data = []
    rows, nextlink = get_data(API_START_URL, API_HEADERS)    
    data = data + rows

    while nextlink:
        print(nextlink)
        rows, nextlink = get_data(nextlink, API_HEADERS)    
        data = data + rows
        
    df = pd.DataFrame(data)
    df.to_csv(outpath)