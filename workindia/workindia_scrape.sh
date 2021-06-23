#!/bin/bash

# Workindia Scrape

# This file compiles the different steps in the process into a single script


# Pass log filedate into first argument
filedate=$1
starttime=$(date +"%m/%d/%Y %H:%M:%S %Z")

dropbox="/India Labor Market Indicators/scraping/Workindia/ec2"


cd /home/ec2-user/workindia/

# Run workindia scrapy script. After that export files to dropbox. Then send email notification
{ scrapy crawl Workindia -o output/mainpage/workindia_mainpage_${filedate}.csv -t csv -a jobcountfile="output/jobcount/workindia_jobcount_${filedate}.csv" && \
  # python3 workindia_details.py --input=output/mainpage/workindia_mainpage_${filedate}.csv --output=output/details/workindia_details_${filedate}.csv && \
  python3 ~/util/export_to_dropbox.py output/mainpage/workindia_mainpage_${filedate}.csv "${dropbox}/mainpage/workindia_mainpage_${filedate}.csv" && \
  python3 ~/util/export_to_dropbox.py log/${filedate}.log "${dropbox}/log/${filedate}.log" && \
  python3 ~/util/export_to_dropbox.py output/jobcount/workindia_jobcount_${filedate}.csv "${dropbox}/jobcount/workindia_jobcount_${filedate}.csv";
  # python3 ~/util/export_to_dropbox.py output/details/workindia_details_${filedate}.csv "${dropbox}/details/workindia_details_${filedate}.csv" ;
 } && 
 { 
	endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	echo -e "Subject: workindia Scrape Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/workindia/ec2/log/${filedate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; \
} || 
{ 
	{ echo "Subject: workindia Scrape Failed"; cat log/${filedate}.log; } | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 
}

