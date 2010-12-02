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
