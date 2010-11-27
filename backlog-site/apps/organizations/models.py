from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models

import datetime

from django.core.exceptions import ObjectDoesNotExist
from projects.models import Project

# Was going to make these pinax groups, but didn't want to bring over the slug based urls for teams, and turns out organizations don't 
# actually have members if we go the team route.

class Organization(models.Model):   
  name = models.CharField( max_length=65 )
  slug = models.SlugField(_('slug'), unique=True)
  creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="organizations_created")
  created = models.DateTimeField(_('created'), default=datetime.datetime.now)
  description = models.TextField(_('description'))
  
  @staticmethod
  def getOrganizationsForUser( user ):
    return Organization.objects.filter( teams__members__user__id = user.id );
    
  def get_url_kwargs(self):
      return {'organization_slug': self.slug}


class Team(models.Model):   
  ACCESS_CHOICES = (
      ('read', 'Read Only'), 
      ('write', 'Read / Write'),
      ('admin', 'Administrator') )
  member_users = models.ManyToManyField(User, through="TeamMember", verbose_name=_('members'))
  organization = models.ForeignKey(Organization, related_name="teams")
  name = models.CharField( max_length=65 )
  access_type = models.CharField( max_length=25 , default="read", choices=ACCESS_CHOICES)

class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name="members", verbose_name=_('team'))
    user = models.ForeignKey(User, related_name="teams", verbose_name=_('user'))

class ProjectTeam(models.Model):
  project = models.ForeignKey( Project, related_name="teams", verbose_name=_('project'))
  team = models.ForeignKey(Team, related_name="projects", verbose_name=_('team'))