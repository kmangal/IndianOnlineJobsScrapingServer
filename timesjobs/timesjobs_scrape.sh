#!/bin/bash

# TimesJobs Scrape

# This file compiles the different steps in the process into a single script


# Pass log filedate into first argument
filedate=$1
starttime=$(date +"%m/%d/%Y %H:%M:%S %Z")

cd /home/ec2-user/jobs_scraping/timesjobs/

# Run shine scrapy script. After that export files to dropbox. Then send email notification
{ python3 timesjobs_main.py --mainpage=output/mainpage/timesjobs_mainpage_${filedate}.csv --jobcount=output/jobcount/timesjobs_jobcount_${filedate}.csv &&
  python3 timesjobs_details.py --input=output/mainpage/timesjobs_mainpage_${filedate}.csv --output=output/details/timesjobs_details_${filedate}.csv &&
  python3 ~/jobs_scraping/util/export_to_dropbox.py \
		output/mainpage/timesjobs_mainpage_${filedate}.csv \
		"/India Labor Market Indicators/scraping/TimesJobs/ec2/mainpage/timesjobs_mainpage_${filedate}.csv" ; \
  python3 ~/jobs_scraping/util/export_to_dropbox.py \
		log/${filedate}.log \ 
		"/India Labor Market Indicators/scraping/TimesJobs/ec2/log/${filedate}.log" ; \
  python3 ~/jobs_scraping/util/export_to_dropbox.py \
		output/jobcount/timesjobs_jobcount_${filedate}.csv \
		"/India Labor Market Indicators/scraping/TimesJobs/ec2/jobcount/timesjobs_jobcount_${filedate}.csv"; \
 } && 
 { 
	endtime=$(date +"%m/%d/%Y %H:%M:%S %Z"); \
	echo -e "Subject: TimesJobs Scrape Completed Successfully\n\nLog file saved in India Labor Market Indicators/scraping/TimesJobs/ec2/log/${filedate}.log\nStart Time: ${starttime}\nEnd Time:  ${endtime}" | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; \
} || 
{ 
	{ echo "Subject: TimesJobs Scrape Failed"; tail -n 200 log/${filedate}.log; } | \
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 
}

