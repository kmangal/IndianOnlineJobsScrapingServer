# India Online Jobs Scraping Server

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
I set up a test environment on my laptop within Anaconda. `conda install m2-base` allows me to access linux commands within my Anaconda environment.

## Misc Notes
* Aasan jobs changed its name to Waah Jobs.
* I changed the timezone for timestamps for the detail page scrapers for Timesjobs and Shine from IST to UTC on July 11th 2021.
