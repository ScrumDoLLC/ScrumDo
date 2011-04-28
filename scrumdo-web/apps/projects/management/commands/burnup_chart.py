#!/usr/bin/env python
from datetime import date, timedelta
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError

from projects.calculation import calculateProject

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = Project.objects.filter(active=True)
        for project in projects:
            try:
                calculateProject( project )
            except:
                logger.error("Could not calculate project %s" % project.slug)
