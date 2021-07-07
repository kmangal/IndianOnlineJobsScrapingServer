pip install rq-scheduler

sudo cp ~/jobs_scraping/install/rqscheduler.service /etc/systemd/system/rqscheduler.service

sudo systemctl start rqscheduler.service
sudo systemctl status rqscheduler.service
sudo systemctl enable rqscheduler.service