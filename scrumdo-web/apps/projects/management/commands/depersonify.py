#!/usr/bin/env python

from apps.projects.models import Project, Iteration, Story, PointsLog, SiteStats
from apps.extras.models import *
from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.DEBUG:
            logger.error("Can only run this on sites in debug mode (for safety!)")
            return

        confirm = raw_input("We're about to devestate this DB making it completely non-production worthy and destroy user data.  Type yes to continue.\n > ")
        if confirm != "yes":
            return

        logger.info("Resetting user email addresses to %s and passwords to klug" % settings.CONTACT_EMAIL)
        for user in User.objects.all():
            user.email = settings.CONTACT_EMAIL
            user.password = "sha1$d4f5f$2ccff0e66fe0090095add4d3e47343aa6b8009b7"
            user.save()

        logger.info("Removing project<->extras mappings")
        ExternalStoryMapping.objects.all().delete()
        ProjectExtraMapping.objects.all().delete()
        ExternalTaskMapping.objects.all().delete()
        ExtraConfiguration.objects.all().delete()
        SyncronizationQueue.objects.all().delete()
        Message.objects.all().delete()
