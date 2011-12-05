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




class Team(models.Model):
    ACCESS_CHOICES = [
        ('read', 'Read Only'),
        ('write', 'Read / Write'),
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),]
    members = models.ManyToManyField(User, verbose_name=_('members'), related_name="teams")
    projects = models.ManyToManyField("projects.Project", verbose_name=_('projects'), related_name="teams")

    organization = models.ForeignKey('Organization', related_name="teams")

    name = models.CharField( max_length=65 )
    access_type = models.CharField( max_length=25 , default="read", choices=ACCESS_CHOICES)

    class Meta:
        ordering = ["name"]
    
    def access_description(self):
        access = [ entry[1] for entry in Team.ACCESS_CHOICES if entry[0]==self.access_type ]
        if len(access) == 1:
            return access[0]
        return "Read Only"

    def hasMember(self, user):
        return self.members.filter(id=user.id).count() > 0
        
    def __unicode__(self):
        return "[%s] %s" % (self.organization.name, self.name)


class TeamInvite(models.Model):
    email_address = models.CharField(max_length=60)
    team = models.ForeignKey(Team, related_name="invites")
    key = models.CharField(max_length=8)


# Was going to make these pinax groups, but didn't want to bring over the slug based urls for teams, and turns out organizations don't
# actually have members if we go the team route.

class Organization(models.Model):
    name = models.CharField( max_length=65 )
    slug = models.SlugField(_('slug'), unique=True)
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="organizations_created")
    created = models.DateTimeField(_('created'), default=datetime.datetime.now)
    description = models.TextField(_('description'),  null=True, default="")
    source = models.CharField(max_length=100, default="", blank=True)

    def activeProjects(self):
        return self.projects.filter(active=True);

    # Returns all organizations
    @staticmethod
    def getOrganizationsForUser( user ):
        return Organization.objects.filter( teams__members = user ).distinct().order_by("name")

    # Returns all organizations the user has admin rights to.
    @staticmethod
    def getAdminOrganizationsForUser( user ):
        return Organization.objects.filter( teams__access_type="admin", teams__members = user ).distinct().order_by("name")

    def getOwnersGroup(self):
        teams = self.teams.filter( access_type="admin" )
        if len(teams) > 0:
            return teams[0]
        return None

    def projectsByCategory(self):
        return self.projects.all().order_by('-active','category','name')

    def hasStaffAccess( self, user ):
        if user.is_staff:
            return True
        if self.creator == user:
            return True
        return (self.teams.filter( access_type="staff", members=user ).count() > 0)

    def hasReadAccess( self, user ):
        if user.is_staff:
            return True
        if self.creator == user:
            return True
        return (self.teams.filter( members=user ).count() > 0)

    def memberCount(self):
        members = []
        for team in self.teams.all():
            for member in team.members.all():
                if members.count(member) == 0:
                    members.append(member)
        return len(members)

    def get_url_kwargs(self):
        return {'organization_slug': self.slug}

    def __unicode__(self):
        return "%s - %s" % (self.slug, self.name)

    def get_absolute_url(self):
        return reverse("organization_detail", kwargs={"organization_slug":self.slug})
