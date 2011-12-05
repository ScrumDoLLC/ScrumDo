#!/usr/bin/env python

# creates a staff team in every organization

from apps.projects.models import Project, Iteration, Story, PointsLog, SiteStats
from apps.extras.models import *
from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from organizations.models import *
from projects.models import Project

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        for organization in Organization.objects.all():
            if organization.teams.filter(access_type="staff").count() > 0:
                continue
            logger.debug("Creating staff team for %s" % organization.slug)
            team = Team(organization=organization,name="Staff",access_type="staff")
            team.save()
            team.members.add(organization.creator)