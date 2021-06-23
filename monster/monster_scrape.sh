#!/bin/bash

# Monster Scrape

# This file compiles the different steps in the process into a single script


# Pass log filedate into first argument
filedate=$1
starttime=$(date +"%m/%d/%Y %H:%M:%S %Z")

cd /home/ec2-user/monster/

# Run monster scrapy script. After that export files to dropbox. Then send email notification
{ scrapy crawl Monster -o output/mainpage/monster_mainpage_${filedate}.csv -t csv -a jobcountfile="output/jobcount/monster_jobcount_${filedate}.csv" && \
  python3 ~/util/export_to_dropbox.py \
		output/mainpage/monster_mainpage_${filedate}.csv \
		"/India Labor Market Indicators/scraping/Monster/ec2/mainpage/monster_mainpage_${filedate}.csv" ; \
  python3 ~/util/export_to_dropbox.py \
		log/${filedate}.log \ 
		"/India Labor Market Indicators/scraping/Monster/ec2/log/${filedate}.log" ; \
  python3 ~/util/export_to_dropbox.py \
		output/jobcount/monster_jobcount_${filedate}.csv \
		"/India Labor Market Indicators/scraping/Monster/ec2/jobcount/monster_jobcount_${filedate}.csv"; \
 } && 
 { 
	endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	echo -e "Subject: Monster Scrape Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/Monster/ec2/log/${filedate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; \
} || 
{ 
	{ echo "Subject: Monster Scrape Failed"; tail -n 200 log/${filedate}.log; } | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 
}

