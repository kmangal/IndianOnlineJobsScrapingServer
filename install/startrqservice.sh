pip install rq-scheduler

sudo mv ~/jobs_scraping/install/rqscheduler.service /etc/systemd/system/rqscheduler.service

sudo systemctl start rqscheduler.service
sudo systemctl status rqscheduler.service
sudo systemctl enable rqscheduler.service