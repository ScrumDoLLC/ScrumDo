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

from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models

import datetime

from django.core.exceptions import ObjectDoesNotExist

from projects.models import Project
from organizations.models import Organization

class Team(models.Model):   
  ACCESS_CHOICES = (
      ('read', 'Read Only'), 
      ('write', 'Read / Write'),
      ('admin', 'Administrator') )
  members = models.ManyToManyField(User, verbose_name=_('members'))
  projects = models.ManyToManyField(Project, verbose_name=_('projects'), related_name="teams")
  
  organization = models.ForeignKey(Organization, related_name="teams")
  
  name = models.CharField( max_length=65 )
  access_type = models.CharField( max_length=25 , default="read", choices=ACCESS_CHOICES)
