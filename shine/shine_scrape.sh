#!/bin/bash

# Shine Scrape

# This file compiles the different steps in the process into a single script


# Pass log filedate into first argument
filedate=$1
starttime=$(date +"%m/%d/%Y %H:%M:%S %Z")

dropbox="/India Labor Market Indicators/scraping/Shine/ec2"


cd /home/ec2-user/shine/

export PYTHONUNBUFFERED=TRUE

# Run shine scrapy script. After that export files to dropbox. Then send email notification
{ scrapy crawl Shine -o output/mainpage/shine_mainpage_${filedate}.csv -t csv -a jobcountfile="output/jobcount/shine_jobcount_${filedate}.csv" && \
  python3 shine_details.py --input=output/mainpage/shine_mainpage_${filedate}.csv --output=output/details/shine_details_${filedate}.csv && \
  python3 ~/util/export_to_dropbox.py output/mainpage/shine_mainpage_${filedate}.csv "${dropbox}/mainpage/shine_mainpage_${filedate}.csv" && \
  python3 ~/util/export_to_dropbox.py log/${filedate}.log "${dropbox}/log/${filedate}.log" && \
  python3 ~/util/export_to_dropbox.py output/jobcount/shine_jobcount_${filedate}.csv "${dropbox}/jobcount/shine_jobcount_${filedate}.csv"&& \
  python3 ~/util/export_to_dropbox.py output/details/shine_details_${filedate}.csv "${dropbox}/details/shine_details_${filedate}.csv" ;
 } && 
 { 
	endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	echo -e "Subject: Shine Scrape Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/Shine/ec2/log/${filedate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; \
} || 
{ 
	{ echo "Subject: Shine Scrape Failed"; tail -n 200 log/${filedate}.log; } | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 
}

