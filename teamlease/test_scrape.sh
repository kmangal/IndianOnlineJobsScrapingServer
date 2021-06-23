#!/bin/bash

# TeamLease  Scrape

# This file compiles the different steps in the process into a single script

# Pass in the filedate as an argument
filedate=$1
starttime=$(date +"%m/%d/%Y %H:%M:%S %Z");

cd /home/ec2-user/teamlease/

# Run teamlease scrapy script. After that, generate report and email it.
{
	scrapy crawl Teamlease -o "test/mainpage/teamlease_mainpage_${filedate}.csv"  -a jobcountfile="test/jobcount/teamlease_jobcount_${filedate}.csv" -a logfile="test/log//${filedate}.log" && \
	python3 ~/util/export_to_dropbox.py \
		test/mainpage/teamlease_mainpage_${filedate}.csv \
		"/India Labor Market Indicators/scraping/TeamLease/ec2/test/mainpage/teamlease_mainpage_${filedate}.csv" ; \
	python3 ~/util/export_to_dropbox.py \
		test/log/${filedate}.log \
		"/India Labor Market Indicators/scraping/TeamLease/ec2/test/log/${filedate}.log" ; \
	python3 ~/util/export_to_dropbox.py \
		test/jobcount/teamlease_jobcount_${filedate}.csv \
		"/India Labor Market Indicators/scraping/TeamLease/ec2/test/jobcount/teamlease_jobcount_${filedate}.csv"; \
 } &&
 { 
	endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	echo -e "Subject: TeamLease Scrape Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/TeamLease/ec2/test/log/${filedate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; \
} || 
{ 
	{ echo "Subject: TeamLease Scrape Failed"; tail -n 200 test/log/${filedate}.log; } | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 
}


