#!/bin/bash

echo "=================================="
echo "      Shine Scrape                "
echo "=================================="

filedate=$(date +'%Y%m%d_%H%M%S')
echo "Log file date: ${filedate}"

cd /home/ec2-user/shine/
ls

export PYTHONUNBUFFERED=TRUE

# Rum the scraper in a backgorund process. Pass the filedate as an argument
nohup ~/shine/shine_scrape.sh ${filedate} > log/${filedate}.log &

exit 0


