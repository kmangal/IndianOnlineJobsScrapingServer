filedate=$(date +'%Y%m%d_%H%M%S')
echo "Log file date: ${filedate}"

cd /home/ec2-user/workindia/
ls

# Rum the scraper in a backgorund process. Pass the filedate as an argument
nohup sh workindia_scrape.sh ${filedate} > log/${filedate}.log &

exit 0
