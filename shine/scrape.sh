#!/bin/bash

echo "=================================="
echo "      Shine Scrape                "
echo "=================================="

filedate=$(date +'%Y%m%d_%H%M%S')
echo "Log file date: ${filedate}"

cd /home/ec2-user/jobs_scraping/shine/

nohup python3 -u shine_scrape.py --full > /dev/null 2>&1 &
