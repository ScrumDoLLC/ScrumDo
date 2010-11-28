from django.core.urlresolvers import reverse
from django.contrib.auth.models import  User
from django.utils.translation import ugettext_lazy as _
from django.db import models

import datetime

from django.core.exceptions import ObjectDoesNotExist


# Was going to make these pinax groups, but didn't want to bring over the slug based urls for teams, and turns out organizations don't 
# actually have members if we go the team route.

class Organization(models.Model):   
  name = models.CharField( max_length=65 )
  slug = models.SlugField(_('slug'), unique=True)
  creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="organizations_created")
  created = models.DateTimeField(_('created'), default=datetime.datetime.now)
  description = models.TextField(_('description'))
  
  def getDefaultTeam():
    return Organization.objects.filter( teams__access_type="admin", teams__members__user__id = user.id ).order_by("name")
  
  # Returns all organizations
  @staticmethod
  def getOrganizationsForUser( user ):
    return Organization.objects.filter( teams__members = user ).order_by("name")

  # Returns all organizations the user has admin rights to.
  @staticmethod
  def getAdminOrganizationsForUser( user ):
    return Organization.objects.filter( teams__access_type="admin", teams__members__user__id = user.id ).order_by("name")

  # returns all organizations the user has read/write access to
  @staticmethod
  def getReadWriteOrganizationsForUser( user ):
    return Organization.objects.filter( teams__access_type__ne="read", teams__members__user__id = user.id ).order_by("name")

    
  def get_url_kwargs(self):
      return {'organization_slug': self.slug}




