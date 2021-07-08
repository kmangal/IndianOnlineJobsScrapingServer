sudo apt update

git config --global credential.helper store
git clone https://github.com/kmangal/jobs_scraping.git

# Provide username and personal access token

git config --global user.name "EC2 Server"
git config --global user.email india.labourinsights.server@gmail.com

cd jobs_scraping
sh install/makefolders.sh

sudo apt install python3-pip -y
sudo apt install python3.8-venv
pip3 install virtualenv
python3 -m venv env
source env/bin/activate

# Install chrome
sudo apt-get install -y chromium-browser
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm ./google-chrome-stable_current_amd64.deb

sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget

cd jobs_scraping
pip install -r requirements.txt


sh install/startrqservice.sh
cp install/.bashrc ~/.bashrc

sh install/startworkers.sh

