from datetime import datetime, date
import time
import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from organizations.models import Organization
# from projects.models import Project, Iteration, Story
from django.template.loader import render_to_string

import logging

logger = logging.getLogger(__name__)

from avatar.templatetags.avatar_tags import avatar_url

class ScrumLog(models.Model):
    TYPE_NOTE=0
    TYPE_GROUP_NOTE=1
    TYPE_SOURCE_CONTROL=2
    GITHUB_ICON=2
    
    creator = models.ForeignKey(User, null=True)
    project = models.ForeignKey("projects.Project", related_name="log_items" )
    date = models.DateTimeField(auto_now_add=True )
    message = models.TextField()
    message_type = models.IntegerField()
    icon = models.IntegerField(default=1)
    flagged = models.BooleanField(default=False)
    def icon_url( self ):
        if self.icon == ScrumLog.GITHUB_ICON:
            return "%simages/octocat.png" % settings.SSL_STATIC_URL 
        if self.message_type == ScrumLog.TYPE_GROUP_NOTE:
            return "%spinax/images/silk/icons/group.png" % settings.SSL_STATIC_URL 
        return avatar_url(self.creator, 16)
        
    def render_text(self):
        return render_to_string("scrum_log/scrum_log_newsfeed.html",{"entry":self,"project":self.project})


# post_save.connect(add_attachment_extra, sender=Attachment)
# post_save.connect(add_subscription, sender=Organization)
# pre_delete.connect(organization_deleted, sender=Organization)
