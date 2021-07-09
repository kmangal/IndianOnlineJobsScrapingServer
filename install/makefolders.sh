cd ~/jobs_scraping/

for var in teamlease timesjobs shine monster
do
	mkdir -p $var/log
	mkdir -p $var/log/mainpage
	mkdir -p $var/log/details
	mkdir -p $var/output
	mkdir -p $var/output/mainpage
	mkdir -p $var/output/jobcount
	mkdir -p $var/output/details
	mkdir -p $var/test
	mkdir -p $var/test/mainpage
	mkdir -p $var/test/jobcount
	mkdir -p $var/test/log
done

mkdir -p waahjobs/test
mkdir -p waahjobs/test/api
mkdir -p waahjobs/test/log
mkdir -p waahjobs/output/api
mkdir -p waahjobs/log

mkdir -p log
mkdir -p log/error
