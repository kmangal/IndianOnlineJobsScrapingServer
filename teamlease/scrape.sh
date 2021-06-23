#!/bin/bash

# TeamLease  Scrape

echo "=================================="
echo "      TeamLease Scrape            "
echo "=================================="

filedate=$(date +'%Y%m%d_%H%M%S')
echo "Log file date: ${filedate}"

cd /home/ec2-user/teamlease/

export PYTHONUNBUFFERED=TRUE

nohup ~/teamlease/teamlease_scrape.sh ${filedate} > log/${filedate}.log &

exit 0


