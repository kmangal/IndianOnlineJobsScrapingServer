#!/bin/bash

# TeamLease  Scrape

# This file compiles the different steps in the process into a single script

# Pass in the filedate as an argument
filedate=$1
starttime=$(date +"%m/%d/%Y %H:%M:%S %Z");

cd /home/ec2-user/teamlease/

export PYTHONUNBUFFERED=TRUE

# Run teamlease scrapy script. After that, generate report and email it.
{
	scrapy crawl Teamlease -o output/mainpage/teamlease_mainpage_${filedate}.csv -t csv -a jobcountfile="output/jobcount/teamlease_jobcount_${filedate}.csv" && \
	python3 ~/util/export_to_dropbox.py \
		output/mainpage/teamlease_mainpage_${filedate}.csv \
		"/India Labor Market Indicators/scraping/TeamLease/ec2/mainpage/teamlease_mainpage_${filedate}.csv" ; \
	python3 ~/util/export_to_dropbox.py \
		log/${filedate}.log \
		"/India Labor Market Indicators/scraping/TeamLease/ec2/log/${filedate}.log" ; \
	python3 ~/util/export_to_dropbox.py \
		output/jobcount/teamlease_jobcount_${filedate}.csv \
		"/India Labor Market Indicators/scraping/TeamLease/ec2/jobcount/teamlease_jobcount_${filedate}.csv"; \
 } &&
 { 
	endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	echo -e "Subject: TeamLease Scrape Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/TeamLease/ec2/log/${filedate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; \
} || 
{ 
	{ echo "Subject: TeamLease Scrape Failed"; tail -n 200 log/${filedate}.log; } | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 
}


