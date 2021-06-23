
find /home/ec2-user/timesjobs/log/* -mtime +14 -exec rm {} \;
find /home/ec2-user/timesjobs/output/* -mtime +14 -exec rm {} \;

