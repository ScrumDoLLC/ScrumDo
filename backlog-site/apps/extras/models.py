from datetime import datetime, date
from django.db import models
import time

from django.core.urlresolvers import reverse
from projects.models import Project, Iteration, Story


# Determines which extras are active for which projects.
# The configuration stores a json object of configuration options to make storing that sort of
# data easier on the extra.
class ProjectExtraMapping( models.Model ):
  project = models.ForeignKey(Project, related_name="extras")
  extra_slug = models.CharField( "extra_slug" , max_length=25)
  configuration = models.TextField( )  


# When an extra imports stories, it should put them into the story queue instead of directly into Story objects.
# this way, the user will be presented with a list of stories that they can choose to use or not from all of their
# external sources.
#
# After a story is imported, the extra should feel free to directly update it on syncronizations.
class StoryQueue( models.Model ):
  project = models.ForeignKey(Project, related_name="story_queue")
  extra_slug = models.CharField( "extra_slug" , max_length=25)
  
  external_id = models.CharField( max_length=40)
  imported_on = models.DateTimeField( default=datetime.now)
  modified = models.DateTimeField( default=datetime.now) 
    
  summary = models.TextField( )  
  detail = models.TextField( blank=True )
  points = models.CharField('points', max_length=3, default="?" ,blank=True)
  status = models.IntegerField( max_length=2, choices=Story.STATUS_CHOICES, default=1 )
  extra_1 = models.TextField( blank=True , null=True)
  extra_2 = models.TextField( blank=True , null=True)
  extra_3 = models.TextField( blank=True , null=True)
  
  
class ExtraConfiguration( models.Model ):
  extra_slug = models.CharField( "extra_slug" , max_length=25)
  project_slug = models.CharField( "project_slug" , max_length=55)
  configuration_pickle = models.TextField( blank=True )