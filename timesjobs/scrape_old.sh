#!/bin/bash

# TimesJobs Scrape

# This file compiles the different steps in the process into a single script

echo "=================================="
echo "      TimesJobs Scrape            "
echo "=================================="

logdate=$(date +'%Y%m%d')
echo "Log file date: ${logdate}"

cd /home/ec2-user/timesjobs/

# Run jobcount/mainpage and then details. After that, generate report and email it.

nohup sh -c '{ logdate=$(date +"%Y%m%d"); starttime=$(date +"%m/%d/%Y %H:%M:%S %Z"); } ; \
	     { python3 -u all_city_main.py && python3 -u detail_scrape.py && \
	       python3 -u export_to_dropbox.py log/${logdate}.log "/India Labor Market Indicators/scraping/TimesJobs/ec2/log/${logdate}.log"; } && \
	     { endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	       echo -e "Subject: TimesJobs Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/TimesJobs/ec2/log/${logdate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	       /usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; } || \
	     { { echo "Subject: TimesJobs Scrape Failed"; cat log/${logdate}.log; } | \
	       /usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; }' \
	     > log/${logdate}.log &
exit 0


