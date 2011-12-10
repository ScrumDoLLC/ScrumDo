#!/usr/bin/env python

# Moves the users from the admin/owners team into staff.

from apps.projects.models import Project, Iteration, Story, PointsLog, SiteStats
from apps.extras.models import *
from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from organizations.models import *
from projects.models import Project
import sys, traceback

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        for organization in Organization.objects.all():
            try:
                staff = organization.teams.get(access_type="staff")
                admin = organization.teams.get(access_type="admin", name="Owners")
                staff_members = staff.members.all()
                for admin_member in admin.members.all():
                    if admin_member in staff_members:
                        continue
                    staff.members.add(admin_member)
                    logger.debug("Adding %s to %s/%s" % (admin_member, staff, organization)  )
                    pass
            except:
                logger.debug("Could not update %s" % organization)
                traceback.print_exc(file=sys.stdout)
                continue
                
