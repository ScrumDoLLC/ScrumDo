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
        logger.info("Resetting user email addresses to %s" % settings.CONTACT_EMAIL)
        for user in User.objects.all():
            user.email = settings.CONTACT_EMAIL
            user.save()
        
        logger.info("Removing project<->extras mappings")
        ExternalStoryMapping.objects.all().delete()
        ProjectExtraMapping.objects.all().delete()
        ExternalTaskMapping.objects.all().delete()
        ExtraConfiguration.objects.all().delete()
        SyncronizationQueue.objects.all().delete()        
        Message.objects.all().delete()
        
