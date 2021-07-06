# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

if [[ "$VIRTUAL_ENV" == "" ]] ; then
            echo "Starting virtual environment"
            cd ~
            source env/bin/activate
fi

cd ~
cd jobs_scraping

# User specific aliases and functions
alias jobs="python ~/jobs_scraping/util/jobs.py"
alias status="python ~/jobs_scraping/util/status.py"

#function seelog { tail -n 5 "$(ls -1r $1/*.log | head -n 1)"; }
#export -f seelog
alias seelog="python ~/jobs_scraping/util/seelog.py"