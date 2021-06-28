cd ~/jobs_scraping/

for f in "teamlease" "timesjobs" "shine" "monster"
do
	mkdir ${var}/log
	mkdir ${var}/output
	mkdir ${var}/output/mainpage
	mkdir ${var}/output/jobcount
	mkdir ${var}/output/details
	mkdir ${var}/test
	mkdir ${var}/test/mainpage
	mkdir ${var}/test/jobcount
	mkdir ${var}/test/log
done