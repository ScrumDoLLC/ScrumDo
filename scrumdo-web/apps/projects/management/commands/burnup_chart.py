#!/usr/bin/env python
from datetime import date, timedelta
from apps.projects.models import Project, Iteration, Story, PointsLog
from django.core.management.base import BaseCommand, CommandError

from projects.calculation import calculateProject    


class Command(BaseCommand):
  def handle(self, *args, **options):
    projects = Project.objects.all()
    for project in projects:
      calculateProject( project )

