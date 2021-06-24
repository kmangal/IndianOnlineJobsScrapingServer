#!/bin/bash

# TeamLease  Scrape

echo "=================================="
echo "      TeamLease Scrape            "
echo "=================================="

filedate=$(date +'%Y%m%d_%H%M%S')
echo "Log file date: ${filedate}"

cd /home/ec2-user/jobs-scraping/teamlease/

nohup python3 -u teamlease_scrape.py --full > /dev/null 2>&1 &


