# India Online Jobs Scraping Server

This repository contains a set of files designed to run as an automated server to continuously scrape various online job portals in India.

There are seperate scripts to handle each website. This repository includes scripts for the following online job portals:
* [Shine](https://www.shine.com/)
* [Work India](https://www.workindia.in/)
* Waah Jobs (previously Asaan Jobs; now no longer operating)
* [Times Jobs](https://www.timesjobs.com/)
* [TeamLease](https://www.teamlease.com/)
* Monster (currently Foundit)

Overall flow:
* The scraper cycles through each of the job portals on a regular cycle.
* The scraper downloads the "main page" listings and keeps track of the overall job count.
* Next, for each of the listings, the code checks whether the "details page" has been visited before, and if not it downlaods the information there. The pages that have been visited before are tracked in a MySQL database.
* The data is automatically saved to Dropbox, and the data from the server is deleted on a regular basis to save storage space.

Features:
* The scraper cycles through user agent headers to avoid getting blocked too quickly
* There are a range of utility files to track the status of the current scrapes and debug problems.

Caveats:
* The code was developed in 2021, so it may be out of date.
* I had trouble getting around the website's bot detection systems, so it was hard to get the code to run continuously.

## Installation

This code is designed to run on an Amazon Linux EC2 instance that uses the Ubunutu operating system. 

- After booting the instance from scratch, run the commands in install/startup-ubuntu.sh to get the system set up. (Note: think of the startup script as more of a record of the commands that were used to set up the server rather than a script that can be run directly. This is because the script includes commands to get git installed and clone the project folder, but those can't be run if this folder isn't on the server already.)

- There is a legacy file in install/startup-rhel.sh that I wrote for a Amazon RHEL-type instance. This instance type was abandoned because it turns out that this OS doesn't natively support Chrome, which we would need to render javascript (either using the `selenium` library or `pyppeteer` library).

## Server administration

I use a [Redis Queue](https://python-rq.org/) to manage tasks on the server.
 - In a new screen (screen - S \[worker name\}) run worker.py to start a worker. I keep 2 - in case one is busy, another one is available.
 - Run main.py to queue up all regular tasks.
 
You can type in the following commands directly in the terminal to manage tasks:
	- status = tells you which tasks are running on which workers, when they started, how long they are running
	- jobs = lists all currently scheduled jobs within the next 7 days. If a task is repeating, only the next immediate instance will be returned.

## Test environment
You can set up a test environment on your local machine within Anaconda. If you're using Windows, run `conda install m2-base` to access linux commands within the Anaconda environment.

## Misc Notes
* Aasan jobs changed its name to Waah Jobs.
* I changed the timezone for timestamps for the detail page scrapers for Timesjobs and Shine from IST to UTC on July 11th 2021.
