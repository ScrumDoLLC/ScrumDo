#!/bin/bash
source /home/ec2-user/backlog-site/pinax-env/bin/activate
python /home/ec2-user/backlog-site/scrumdo-web/manage.py send_mail >/dev/null
