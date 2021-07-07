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
sh install/makefolders.sh

pip install -r requirements.txt

sh install/startrqservice.sh

cp install/.bashrc ~/.bashrc


# chromium install
# source: https://stackoverflow.com/questions/48480143/installing-chromium-on-amazon-linux
sudo amazon-linux-extras install epel -y
sudo yum install -y chromium

sh install/startworkers.sh
