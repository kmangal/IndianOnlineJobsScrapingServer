pip3 install virtualenv
python3 -m venv env
source env/bin/activate

sudo yum install git -y

git config --global credential.helper store
git clone https://github.com/kmangal/jobs_scraping.git
# Provide username and personal access token

cd jobs_scraping
sh util/makefolders.sh

pip install scrapy
pip install bs4

