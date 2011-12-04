from django.db import models
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import  User
from django.core.cache import cache
import sys, traceback
from itertools import groupby

from scrumdo_model_utils.models import InheritanceCastModel

import datetime
import traceback
import logging

logger = logging.getLogger(__name__)

class ProjectEmailSubscription(models.Model):
    project = models.ForeignKey("projects.Project")
    user = models.ForeignKey(User,related_name="email_subscriptions")
    def __unicode__(self):
        return "Subscription: %s %s" % (self.user, self.project)

class NewsItem(models.Model):
    created = models.DateTimeField(_('created'), default=datetime.datetime.now)
    user = models.ForeignKey(User,related_name="newsItems", null=True, blank=True)
    project = models.ForeignKey("projects.Project", related_name="newsItems", null=True, blank=True)
    text = models.TextField()
    icon = models.CharField(max_length=24)
    feed_url = models.CharField(max_length=75, null=True, blank=True)
    @staticmethod
    def purgeOld(days=365):
        today = datetime.date.today()
        mdiff = datetime.timedelta(days=-days)
        date_30days_Agoago = today + mdiff
        NewsItem.objects.filter(created__lte=date_30days_Agoago).delete()
        
    class Meta:
        ordering = [ '-created' ]