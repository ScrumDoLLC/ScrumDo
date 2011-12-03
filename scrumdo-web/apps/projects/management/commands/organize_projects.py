#!/usr/bin/env python

# creates a new organization for every project that doesn't have one

from apps.projects.models import Project, Iteration, Story, PointsLog, SiteStats
from apps.extras.models import *
from mailer.models import Message
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from organizations.models import *
from projects.models import Project

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        user_org_map = {}
        projects = Project.objects.filter(organization=None)
        logger.debug("%d projects" % projects.count() )
        for project in projects:
            if project.creator.username in user_org_map:
                logger.debug("Found organization for %s" % project.creator.username)
                organization = user_org_map[ project.creator.username ]
            else:
                logger.debug("Creating organization for %s" % project.creator.username)
                # organization = user_org_map[ project.creator.username ]
                
                # name = models.CharField( max_length=65 )
                #   slug = models.SlugField(_('slug'), unique=True)
                #   creator = models.ForeignKey(User, verbose_name=_('creator'), related_name="organizations_created")
                #   created = models.DateTimeField(_('created'), default=datetime.datetime.now)
                #   description = models.TextField(_('description'),  null=True, default="")
                #   source = models.CharField(max_length=100, default="", blank=True)
                
                organization = Organization(name="%s's Default Organization" % project.creator.username,
                                            slug="def_org_%s" % project.creator.id,
                                            creator=project.creator,
                                            description="Auto generated organization for %s" % project.creator.username,
                                            source = "" )
                organization.save()
                default_team = Team(organization = organization, name="Owners", access_type="admin")
                default_team.save()

                default_team.members.add(project.creator)

                member_team = Team(organization = organization, name="Members", access_type="write")
                member_team.save()
                
                user_org_map[ project.creator.username ] = organization
                
            project.organization = organization
            for team in organization.teams.all():
                team.projects.add(project)
            project.save()