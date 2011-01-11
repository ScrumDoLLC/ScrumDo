#!/bin/bash
source /home/ec2-user/backlog-site/pinax-env/bin/activate
python /home/ec2-user/backlog-site/backlog-site/manage.py site_stats
