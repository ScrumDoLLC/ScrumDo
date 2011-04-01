#!/usr/bin/env python
import sys
from datetime import date, timedelta

from os.path import abspath, dirname, join

from django.core.management.base import BaseCommand, CommandError

from projects.access import *
from projects.models import *
from organizations.models import *

from django.contrib.auth.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        for project in Project.objects.all():
            print "Project %s " % project.slug
            for user in User.objects.all():
                if has_admin_access(project, user):
                    print "  Admin:  %s" % user.username
                if has_write_access(project, user):
                    print "  Write:  %s" % user.username
                if has_read_access( project, user):
                    print "  Read:  %s" % user.username
