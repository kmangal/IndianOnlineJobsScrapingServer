
from requests_html import HTMLSession

import asyncio


def get_element(response, css):
    m = response.find(css)
    if m:
        return m[0].text
    else:
        return 'MISSING'
            
header =  {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
        "Accept-Encoding": "gzip, deflate", 
        "Accept-Language": "en,en-US;q=0.9,en;q=0.8", 
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36", 
        }

session = HTMLSession()

url = 'http://www.shine.com/jobs/customer-service-executive/prism-manpower-services/10321840/'
r = session.get(url, headers = header)

r.html.render()
response = r.html 

title = get_element(response, '.cls_jobtitle')
top_rhs = response.find('.jobDate')

print(title)
print(top_rhs)

session.close()

