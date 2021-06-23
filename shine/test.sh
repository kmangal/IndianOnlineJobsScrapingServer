#!/bin/bash

# Shine Scrape

# This file compiles the different steps in the process into a single script

echo "=================================="
echo "      Shine Scrape                "
echo "=================================="

filedate=$(date +'%Y%m%d_%H%M%S')
echo "Log file date: ${filedate}"

cd /home/ec2-user/shine/

# Run shine scrapy script. After that, generate report and email it.

nohup sh -c \
'{ filedate=$(date +"%Y%m%d_%H%M%S"); starttime=$(date +"%m/%d/%Y %H:%M:%S %Z"); } ; \
 { 
	scrapy crawl Shine -O test/mainpage/shine_mainpage_${filedate}.csv -t csv -a debug=True -a jobcountfile="test/jobcount/shine_jobcount_${filedate}.csv" && \
	python3 export_to_dropbox.py test/mainpage/shine_mainpage_${filedate}.csv "/India Labor Market Indicators/scraping/Shine/ec2/test/mainpage/shine_mainpage_${filedate}.csv" ; \
	python3 export_to_dropbox.py test/log/${filedate}.log "/India Labor Market Indicators/scraping/Shine/ec2/test/log/${filedate}.log" ; \
	python3 export_to_dropbox.py test/jobcount/shine_jobcount_${filedate}.csv "/India Labor Market Indicators/scraping/Shine/ec2/test/jobcount/shine_jobcount_${filedate}.csv"; \
 } && \
 { 
	endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	echo -e "Subject: Shine Scrape Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/Shine/ec2/test/log/${filedate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; \
} || \
{ 
	{ echo "Subject: Shine Scrape Failed"; cat test/log/${filedate}.log; } | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 
}' \
> test/log/${filedate}.log &

exit 0


