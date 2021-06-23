#!/bin/bash

#Argument 1 = local folder
#Argument 2 = dropbox folder

runtime=$(date +'%m/%d/%Y %H:%M:%S %Z')
python3 ~/util/cleanfolder.py "$1" "$2" --verbose | 
	(echo "Subject: Cleaned Folder ${1}" && echo "Script ran at: ${runtime}" && cat) |
	/usr/sbin/sendmail -f india.labourinsights.server@gmail.com -F "India Labour Insights Server" india.labourinsights.server@gmail.com; 


