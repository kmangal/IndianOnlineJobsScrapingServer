#!/bin/bash

# TeamLease  Scrape

echo "=================================="
echo "      TeamLease Scrape            "
echo "=================================="

filedate=$(date +'%Y%m%d_%H%M%S')
echo "Log file date: ${filedate}"

export PYTHONUNBUFFERED=TRUE

nohup ~/teamlease/teamlease_scrape.sh ${filedate} > log/latest_scrape.log &


