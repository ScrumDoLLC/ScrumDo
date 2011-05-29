#!/bin/bash
source /home/ec2-user/ScrumDo/pinax-env/bin/activate
python /home/ec2-user/ScrumDo/scrumdo-web/manage.py retry_deferred
