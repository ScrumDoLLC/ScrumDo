#!/usr/bin/env python

# ScrumDo - Agile/Scrum story management web application 
# Copyright (C) 2011 ScrumDo LLC
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA



# This script handles running the extra's syncronization logic.
# You should set this up on some sort of scheduled basis.  The
# scrumdo.com website runs it once a minute.

import sys
from datetime import date, timedelta

from apps.projects.models import Project, Iteration, Story, PointsLog
from apps.extras.models import ProjectExtraMapping, SyncronizationQueue
from apps.extras.manager import manager
import string
import logging
import sys, traceback
import getopt
import random
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        for project in Project.objects.all():
            project.token = "".join(random.sample(string.lowercase + string.digits, 7))
            project.save()