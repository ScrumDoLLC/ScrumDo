#!/usr/bin/env python

from apps.projects.models import Project, Iteration, Story, PointsLog, SiteStats
from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        stats = SiteStats()
        stats.project_count = Project.objects.count()
        stats.user_count = User.objects.count()
        stats.story_count = Story.objects.count()
        stats.save()
