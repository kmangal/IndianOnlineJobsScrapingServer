cd ~/jobs_scraping/

for var in teamlease timesjobs shine monster
do
	mkdir -p $var/log
	mkdir -p $var/output
	mkdir -p $var/output/mainpage
	mkdir -p $var/output/jobcount
	mkdir -p $var/output/details
	mkdir -p $var/test
	mkdir -p $var/test/mainpage
	mkdir -p $var/test/jobcount
	mkdir -p $var/test/log
done