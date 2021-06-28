pip3 install virtualenv
python3 -m venv env
source env/bin/activate

sudo yum install git -y

git config --global credential.helper store
git clone https://github.com/kmangal/jobs_scraping.git
# Provide username and personal access token

git config --global user.name "EC2 Server"
git config --global user.email india.labourinsights.server@gmail.com

cd jobs_scraping
sh util/makefolders.sh

